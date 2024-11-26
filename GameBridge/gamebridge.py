import subprocess
import socket
import threading
import sys
import queue
import hashlib


class GameBridge:
    def __init__(self, host='127.0.0.1', port=25564):
        """
        Initializes the server with socket configurations.

        :param host: Host for the socket server.
        :param port: Port for the socket server.
        """
        self.host = host
        self.port = port
        self.server = None
        self.executables = {}
        self.active_processes = {}
        self.output_queues = {}
        self.auth_credentials = {}

    def set_credentials(self, username, password):
        """
        Sets basic authentication credentials.

        :param username: Username for authentication.
        :param password: Password for authentication.
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.auth_credentials[username] = hashed_password

    def _authenticate_client(self, client_socket):
        """
        Authenticates a client using basic authentication.

        :param client_socket: The client's socket connection.
        :return: True if authentication succeeds, False otherwise.
        """
        client_socket.sendall(b"Username: ")
        username = client_socket.recv(1024).decode().strip()

        client_socket.sendall(b"Password: ")
        password = client_socket.recv(1024).decode().strip()

        client_socket.sendall(b"\033[F\033[KPassword: ********\n")

        if username in self.auth_credentials:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if self.auth_credentials[username] == hashed_password:
                client_socket.sendall(b"Authentication successful.\n")
                return True

        client_socket.sendall(b"Authentication failed.\n")
        return False

    def add_server(self, name, exe_path, args=None, working_dir=None, start_immediately=True):
        """
        Adds an executable to the server's list of available executables.

        :param name: Name to identify the executable.
        :param exe_path: Path to the executable.
        :param args: List of arguments to pass to the executable.
        :param working_dir: Working directory for the executable.
        :param start_immediately: Whether to start the executable immediately.
        """
        self.executables[name] = {
            "exe_path": exe_path,
            "args": args or [],
            "working_dir": working_dir
        }

        if start_immediately:
            self._start_executable(name, distribute_output=True)

    def _start_executable(self, name, distribute_output=False):
        """
        Starts the specified executable process.

        :param name: Name of the executable to start.
        :param distribute_output: Whether to distribute output to clients.
        """
        if name in self.active_processes:
            print(f"Executable '{name}' is already running.")
            return

        if name not in self.executables:
            print(f"Executable '{name}' not found.", file=sys.stderr)
            return

        exe_config = self.executables[name]
        command = [exe_config["exe_path"]] + exe_config["args"]

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=exe_config["working_dir"]
            )
            self.active_processes[name] = process
            self.output_queues[name] = queue.Queue()
            print(f"Executable '{name}' started immediately.")

            if distribute_output:
                threading.Thread(
                    target=self._read_process_output,
                    args=(process, name),
                    daemon=True
                ).start()
        except FileNotFoundError:
            print(f"Error: Executable '{
                  exe_config['exe_path']}' not found.", file=sys.stderr)
        except Exception as e:
            print(f"Error starting executable '{name}': {e}", file=sys.stderr)

    def _read_process_output(self, process, name):
        """
        Reads the output of a process and stores it in the output queue.

        :param process: The subprocess to read output from.
        :param name: Name of the executable (for tagging the output).
        """
        def read_stream(stream, stream_name):
            try:
                while process.poll() is None:
                    line = stream.readline()
                    if not line:
                        break
                    output_line = f"[{name}] {line}"
                    self.output_queues[name].put(output_line)
                    sys.stdout.write(output_line)
                    sys.stdout.flush()
            finally:
                try:
                    stream.close()
                except Exception as e:
                    print(f"Error closing stream {
                          stream_name}: {e}", file=sys.stderr)

        threading.Thread(target=read_stream, args=(
            process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=read_stream, args=(
            process.stderr, "STDERR"), daemon=True).start()

    def start(self):
        """
        Starts the socket server and listens for incoming connections.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server.accept()
                print(f"Connection from {client_address}")
                threading.Thread(
                    target=self._handle_client, args=(
                        client_socket,), daemon=True
                ).start()
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)
        finally:
            self._cleanup()

    def _handle_client(self, client_socket):
        """
        Handles communication with a connected client.

        :param client_socket: The client's socket connection.
        """
        process = None
        input_queue = queue.Queue()

        def enqueue_input():
            while process and process.poll() is None:
                try:
                    data = input_queue.get(timeout=0.1)
                    process.stdin.write(data)
                    process.stdin.flush()
                except queue.Empty:
                    continue

        def send_output_to_client():
            while process:
                try:
                    # Check if the process is still running
                    if process.poll() is not None:
                        client_socket.sendall(b"Process terminated.\n")
                        break

                    output_line = self.output_queues[chosen_exe].get(
                        timeout=0.1)
                    client_socket.sendall(output_line.encode())
                except queue.Empty:
                    continue
                except BrokenPipeError:
                    print("Client disconnected unexpectedly.", file=sys.stderr)
                    break
        try:
            if not self._authenticate_client(client_socket):
                return

            client_socket.sendall(b"Available executables:\n")
            for name in self.executables.keys():
                client_socket.sendall(f"- {name}\n".encode())
            client_socket.sendall(
                b"Enter the name of the executable to attach:\n")
            chosen_exe = client_socket.recv(1024).decode().strip()

            if chosen_exe not in self.executables:
                client_socket.sendall(
                    b"Invalid executable name. Connection closing.\n")
                return

            if chosen_exe not in self.active_processes:
                self._start_executable(chosen_exe, distribute_output=True)

            process = self.active_processes[chosen_exe]
            threading.Thread(target=enqueue_input, daemon=True).start()
            threading.Thread(target=send_output_to_client, daemon=True).start()

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                input_queue.put(data.decode())

        except Exception as e:
            print(f"Client error: {e}", file=sys.stderr)
        finally:
            try:
                client_socket.close()
            except Exception as e:
                print(f"Error closing client socket: {e}", file=sys.stderr)

    def _cleanup(self):
        """Clean up resources like the server socket and subprocesses."""
        if self.server:
            self.server.close()
        # Use list to avoid modifying while iterating
        for process in list(self.active_processes.values()):
            if process:
                process.terminate()
                try:
                    if process.stdout:
                        process.stdout.close()
                    if process.stderr:
                        process.stderr.close()
                    if process.stdin:
                        process.stdin.close()
                except Exception as e:
                    print(f"Error closing subprocess streams: {
                          e}", file=sys.stderr)
        self.active_processes.clear()


# Example usage
if __name__ == "__main__":
    gb = GameBridge(host='0.0.0.0', port=12345)

    gb.set_credentials("admin", "password")
    gb.set_credentials("admin2", "password2")

    gb.add_server(
        name="Vanilla",
        exe_path="/usr/bin/java",
        args=['-jar', '-Xmx1G', '-Xms1G', 'server.jar', 'nogui'],
        working_dir='/home/srcthird/Documents/Python/minecraft/vanilla/'
    )
    gb.add_server(
        name="Test Executable",
        exe_path="/usr/bin/echo",
        args=["Hello, World!"],
        start_immediately=False
    )
    # gb.add_server(
    #     name="Creative",
    #     exe_path="/usr/bin/java",
    #     args=['-jar', '-Xmx1G', '-Xms1G', 'server.jar', 'nogui'],
    #     working_dir='/servers/minecraft/creative/'
    # )
    gb.start()
