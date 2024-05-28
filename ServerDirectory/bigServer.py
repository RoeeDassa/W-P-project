import pickle
import threading
from user_authentication import UserAuthentication
from server_constants import *
import struct
from server_protocol import Protocol

"""
Name: bigServer
Author: Roee Dassa
Explanation: file receives data from the user and
responds accordingly (adds the data to the appropriate database /
returns relevant data to the user) 
"""


class BigServer:
    def __init__(self):
        # Set instance of UserAuthentication
        self.user_auth = UserAuthentication()

        # Set up the server socket
        self.server_address = (BIG_SERVER_IP_SERVER, BIG_SERVER_PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen()

    def handle_clients(self):
        # Handle incoming client connections in a separate thread
        print("BigServer is now listening for requests...")
        done = False
        while not done:
            try:
                conn, addr = self.server_socket.accept()
                clnt_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(conn, addr))
                clnt_thread.start()
            except socket.error as socket_exception:
                raise RuntimeError("Socket error") from socket_exception
            except Exception as err:
                raise RuntimeError("General error") from err
        self.server_socket.close()

    def handle_single_client(self, conn, addr):
        # Handle each client in a separate thread
        with conn:
            # data = conn.recv(CHUNK_SIZE_L)
            data = Protocol.recv(conn)
            received_data = pickle.loads(data)
            action = received_data.get('action', '')
            if action == 'signup':
                self.user_auth.create_user_data(received_data['username'],
                                                received_data['password'])
                is_legal = self.user_auth.is_info_legal(
                    received_data['username'], received_data['password'])
                Protocol.send_bin(conn,
                                  pickle.dumps('OK' if is_legal else 'NO'))
            elif action == 'login':
                is_user = self.user_auth.check_user_exists(
                    received_data['username'], received_data['password'])
                # conn.send(pickle.dumps('OK' if is_user else 'NO'))
                Protocol.send_bin(conn,
                                  pickle.dumps('OK' if is_user else 'NO'))
            elif action == "add_banned_site":
                self.user_auth.add_banned_site(received_data['username'],
                                               received_data['site'])
                Protocol.send_bin(conn, pickle.dumps('OK'))
            elif action == "remove_banned_site":
                self.user_auth.remove_banned_site(received_data['username'],
                                                  received_data['site'])
                Protocol.send_bin(conn, pickle.dumps('OK'))
            elif action == 'get_banned_sites':
                sites = self.user_auth.get_banned_sites(
                    received_data['username'])
                # conn.send(pickle.dumps(sites))
                Protocol.send_bin(conn, pickle.dumps(sites))

    def handle_signup(self, conn, data):
        # Handle user signup request
        username = data.get('username')
        password = data.get('password')

        print(f"Handling signup for user: {username}")

        # Check if the user already exists in the authentication system
        if self.user_auth.check_user_exists(username, password):
            print("User already exists")
            # conn.sendall(struct.pack('?', False))
            Protocol.send_bin(conn, struct.pack('?', False))
        else:
            print("User does not exist. Proceeding with signup.")
            user_data = self.user_auth.create_user_data(username, password)

            if user_data is None:
                print("Username or Password are not allowed")
                print("Username must consist of alphabetical characters only")
                print(
                    "Password must be at least 8 characters "
                    "long and include letters, numbers, "
                    "and special characters")
                # Notify the client about the signup failure
                # conn.sendall(struct.pack('?', False))
                Protocol.send_bin(conn, struct.pack('?', False))
            else:
                response = "OK"
                # conn.sendall(pickle.dumps(response))
                Protocol.send_bin(conn, pickle.dumps(response))

    def handle_login(self, conn, data):
        # Handle user login request
        username = data.get('username')
        password = data.get('password')

        # Check if the user exists in the authentication system
        is_user = self.user_auth.check_user_exists(username, password)

        # If the user exists, send a confirmation message
        if is_user:
            response = "OK"
            # conn.sendall(pickle.dumps(response))
            Protocol.send_bin(conn, pickle.dumps(response))
        else:
            response = "NO"
            # conn.sendall(pickle.dumps(response))
            Protocol.send_bin(conn, pickle.dumps(response))

    def handle_set_response_port(self, conn, data):
        # Handle user request to set a response port
        response_port = data.get('port')

        try:
            response_socket = socket.socket(socket.AF_INET,
                                            socket.SOCK_STREAM)
            response_socket.connect((BIG_SERVER_IP_SERVER, response_port))

            # Send a response (e.g., acknowledgment) to the client
            # response_socket.sendall(b'OK')
            Protocol.send_bin(response_socket, b'OK')

            response_socket.close()

        except ConnectionRefusedError:
            print("Connection to the client's response port refused.")

        except Exception as e:
            print("Error in handle_set_response_port:", e)

        conn.close()


if __name__ == '__main__':
    big_server = BigServer()
    big_server.handle_clients()
