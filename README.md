# GameBridge
GameBridge is a flexible and easy to use application designed to manage game servers, like Minecraft, Project Zomboid or Valheim remotely. It provides a seamless interface to interact with game server executables from a socket connection, featuring basic authentication, real-time input/output management, and multi-executable support.

## Features

- **Multi-Executable Management**: Run and manage multiple game server executables simultaneously.
- **Real-Time Communication**: Send commands and receive output from game servers in real-time.
- **Basic Authentication**: Secure access to your game servers with username and password.
- **Start-on-Demand or Immediately**: Start executables automatically or wait for client connections.
- **Cross-Platform Support**: Compatible with Windows, macOS, and Linux.

## Use Cases

GameBridge is ideal for:
- Managing Minecraft servers or other game servers.
- Providing a centralized interface for server monitoring and control.
- Offering secure, authenticated access to server admins.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SRCthird/GameBridge.git
   cd GameBridge
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.12+ installed. This was created entirely with the standard library, so no pip installation required

3. **Run the Application**:
   ```bash
   python .
   ```

---

## Usage

### Adding Game Servers

To add game servers (executables), modify the `gamebridge.py` file or use the template in the `Example` section below.

```python
server = GameBridge(port=12345)
server.set_credentials("admin", "password")
server.add_executable(
    name="Minecraft Server 1",
    exe_path="/path/to/minecraft/server1.jar",
    args=["-Xmx2G", "-Xms2G"],
    working_dir="/path/to/server1/",
    start_immediately=True
)
server.add_executable(
    name="Minecraft Server 2",
    exe_path="/path/to/minecraft/server2.jar",
    args=["-Xmx4G", "-Xms4G"],
    working_dir="/path/to/server2/",
    start_immediately=False
)
server.start()
```

### Authentication

GameBridge requires basic authentication. Set usernames and passwords using the `set_credentials` method. Credentials are stored securely using SHA-256 hashing.

---

## Communication

### Connecting to GameBridge
Use a terminal or a custom client to connect to GameBridge:

1. **Connect via Socket**:
   ```bash
   telnet <host> <port>
   ```

2. **Authenticate**:
   Enter your username and password.

3. **Select a Server**:
   Choose an available executable to interact with.

4. **Send Commands**:
   Type commands to send to the game server (e.g., `say Hello World` for Minecraft).

---

## Example Workflow

1. **Client Connects**:
   ```plaintext
   $ telnet 127.0.0.1 12345
   ```
2. **Authentication**:
   ```plaintext
   Username: admin
   Password: [hidden]
   Authentication successful.
   ```
3. **Select a Server**:
   ```plaintext
   Available executables:
   - Minecraft Server 1
   - Minecraft Server 2
   Enter the name of the executable to attach:
   Minecraft Server 1
   ```
4. **Interact with the Server**:
   ```plaintext
   say Hello Players
   [Minecraft Server 1 STDOUT] [Server] Hello Players
   ```

---

## Contributing

We welcome contributions! To get started:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request.

---

## License

GameBridge is licensed under the [MIT License](LICENSE).

---

## Future Plans

- Add support for advanced server analytics.
- Enhance authentication with token-based systems.
- Web-based UI for easier management.

---

## Acknowledgments

GameBridge was inspired by the need for streamlined game server management, particularly for Minecraft. Special thanks to the open-source community for their invaluable tools and resources.

### Next Steps:
1. Replace `https://github.com/yourusername/GameBridge.git` with your actual repository URL.
2. Add a `requirements.txt` file with any dependencies (`hashlib` is part of Python’s standard library, so no extra dependencies are needed unless you add more features).
