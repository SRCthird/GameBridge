import hashlib
import threading
import unittest
from unittest.mock import patch, MagicMock
from GameBridge import GameBridge


class TestGameBridge(unittest.TestCase):
    def setUp(self):
        """Set up a GameBridge instance for testing."""
        self.bridge = GameBridge(host='127.0.0.1', port=25565)
        self.bridge.set_credentials('testuser', 'testpassword')

    def test_set_credentials(self):
        """Test setting authentication credentials."""
        self.assertIn('testuser', self.bridge.auth_credentials)
        hashed_password = self.bridge.auth_credentials['testuser']
        self.assertEqual(
            hashed_password,
            hashlib.sha256('testpassword'.encode()).hexdigest()
        )

    def test_authenticate_client_success(self):
        """Test successful client authentication."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b'testuser\n', b'testpassword\n']

        with patch('builtins.input', side_effect=['testuser', 'testpassword']):
            result = self.bridge._authenticate_client(mock_socket)
            self.assertTrue(result)
            mock_socket.sendall.assert_called_with(
                b"Authentication successful.\n")

    def test_authenticate_client_failure(self):
        """Test failed client authentication."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b'wronguser\n', b'wrongpassword\n']

        result = self.bridge._authenticate_client(mock_socket)
        self.assertFalse(result)
        mock_socket.sendall.assert_called_with(b"Authentication failed.\n")

    @patch('subprocess.Popen')
    def test_add_server_start_immediately(self, mock_popen):
        """Test adding a server with start_immediately=True."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        self.bridge.add_server(
            name="TestServer",
            exe_path="/usr/bin/echo",
            args=["Hello, World!"],
            start_immediately=True
        )
        self.assertIn("TestServer", self.bridge.active_processes)
        mock_popen.assert_called_once()

    def test_add_server_start_later(self):
        """Test adding a server with start_immediately=False."""
        self.bridge.add_server(
            name="DelayedServer",
            exe_path="/usr/bin/echo",
            args=["Delayed Start"],
            start_immediately=False
        )
        self.assertNotIn("DelayedServer", self.bridge.active_processes)
        self.assertIn("DelayedServer", self.bridge.executables)

    @patch('socket.socket')
    def test_start_server(self, mock_socket):
        """Test starting the socket server."""
        mock_server_socket = MagicMock()
        mock_socket.return_value = mock_server_socket
        mock_server_socket.accept.return_value = (
            MagicMock(), ("127.0.0.1", 12345))

        with patch.object(self.bridge, "_handle_client", return_value=None):
            threading.Thread(target=self.bridge.start, daemon=True).start()

        mock_server_socket.bind.assert_called_once_with(('127.0.0.1', 25565))
        mock_server_socket.listen.assert_called_once()

    @patch('subprocess.Popen')
    def test_start_executable(self, mock_popen):
        """Test starting an executable."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        self.bridge.add_server(
            name="ManualStart",
            exe_path="/usr/bin/echo",
            args=["Manual Start"],
            start_immediately=False
        )
        self.bridge._start_executable("ManualStart")

        self.assertIn("ManualStart", self.bridge.active_processes)
        mock_popen.assert_called_once()

    def tearDown(self):
        """Clean up resources after each test."""
        self.bridge._cleanup()


if __name__ == "__main__":
    unittest.main()

