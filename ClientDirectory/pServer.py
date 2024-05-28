import threading
from client_constants import *
import winreg
import pickle
import webbrowser
import time
import subprocess
import urllib.parse
import tldextract
from client_protocol import Protocol

"""
Name: pServer
Author: Roee Dassa
Explanation: proxy server file that tracks
the users site history and blocks them from
designated sites
"""


class ProxyServer:
    def __init__(self, host, port, banned_sites):
        # Initialize list to store the banned sites
        self.banned_sites = banned_sites
        # Initialize a dictionary variable to store the time
        # each site has been banned
        self.banned_times = {site: 0 for site in banned_sites}
        # Initialize the ProxyServer with a host (IP address) and port.
        self.host = host
        self.port = port
        # Create a socket for incoming connections,
        # bind it to the specified host and port, and listen for up to 5
        # connections
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(NUMBER_FIVE)
        # A lock to manage access to banned sites
        self.lock = threading.Lock()

    def update_banned_sites(self):
        while True:
            time.sleep(3)  # Wait for 3 seconds before each update
            new_banned_sites = self.initiate_login.get_banned_sites(
                self.username)
            with self.lock:
                self.banned_sites = new_banned_sites
                self.banned_times = {site: 0 for site in new_banned_sites}

    def handle_client(self, client_socket):
        # Function to handle each client's requests.
        # Receive and decode the client's request (HTTP GET or CONNECT).
        request = client_socket.recv(CHUNK_SIZE_L).decode(UTF8)
        request_lines = request.split('\n')
        first_line = request_lines[NUMBER_ZERO].strip()
        print(request)

        if first_line.startswith(GET_TYPE):
            # If the request is an HTTP GET,
            # extract and print the requested URL.
            url = first_line.split(' ')[NUMBER_ONE]
            print(f'URL requested: {url}')
            self.handle_http_get(client_socket, request)
        elif first_line.startswith(CONNECT_TYPE):
            # If the request is an HTTP CONNECT
            # (for HTTPS), extract and print the requested host.
            _, host_port_protocol = first_line.split(' ', NUMBER_ONE)
            host_port = host_port_protocol.split()[NUMBER_ZERO]
            print(f'Host requested: {host_port}')
            self.handle_https_connect(client_socket, first_line)

    def handle_http_get(self, client_socket, request):
        # Handle HTTP GET requests
        is_banned = False
        url = request.split(' ')[NUMBER_ONE]
        webserver, port = self.parse_url(url)
        domain = urllib.parse.urlparse(url).netloc
        is_banned = any(banned_site in domain.lower() for banned_site in
                        self.banned_sites)

        if is_banned:
            # Send a 403 forbidden poster
            # if a banned site is found in the URL
            with open('errorPage.html', 'r') as file:
                html_content = ""
                while True:
                    chunk = file.read(CHUNK_SIZE_S)
                    html_content += chunk
                    if not chunk:
                        break
            custom_response = "HTTP/1.1 403 Forbidden" + \
                              "\r\nContent-Type: text/html" \
                              "\r\nContent-Length: " \
                              + str(len(html_content)) \
                              + "\r\n\r\n" \
                              + html_content
            client_socket.send(custom_response.encode())
        else:
            # Process the request as usual
            self.proxy_server(webserver, port, client_socket,
                              request.encode())

    def extract_domain(self, url):
        # This function uses tldextract to get the base domain from a URL.
        extracted = tldextract.extract(url)
        # Combine the domain and suffix to get the base domain.
        return "{}.{}".format(extracted.domain, extracted.suffix)

    def handle_https_connect(self, client_socket, first_line):
        _, host_port_protocol = first_line.split(' ', 1)
        host_port = host_port_protocol.split()[NUMBER_ZERO]
        url = "https://" + host_port

        domain = self.extract_domain(url)
        print(f"Extracted domain: {domain}")
        is_banned = any(
            banned_site in domain for banned_site in self.banned_sites)

        if is_banned:
            print("Domain is banned. Checking timing...")
            current_time = time.time()
            with self.lock:
                last_banned_time = self.banned_times.get(domain, 0)
                time_since_last_ban = current_time - last_banned_time
                print(f"Time since last ban: {time_since_last_ban} seconds")

                if time_since_last_ban < 15:
                    print("Less than 15 seconds since last ban.")
                    client_socket.send(b'HTTP/1.1 403 Forbidden\r\n\r\n')
                    client_socket.close()
                    return
                else:
                    # Update the last banned time
                    print(
                        "More than 15 seconds since last ban, updating time "
                        "and showing page.")
                    self.banned_times[domain] = current_time
                    webbrowser.open_new_tab(file_url)

            # Send forbidden response after updating time
            client_socket.send(b'HTTP/1.1 403 Forbidden\r\n\r\n')
            client_socket.close()
        else:
            self.proxy_https(host_port.split(':')[0],
                             int(host_port.split(':')[1]), client_socket)

    def clear_banned_times(self):
        # Clear banned_times dictionary every 5 seconds
        while True:
            time.sleep(150)
            self.banned_times.clear()

    def parse_url(self, url):
        # Function to parse the URL and extract the host and port.
        parts = url.split('/')
        host_port = parts[NUMBER_TWO]
        if ':' in host_port:
            host, port = host_port.split(':')
            return host, int(port)
        else:
            # Default to port 80 for HTTP if no port is specified in the URL.
            return host_port, PORT_80

    def proxy_server(self, webserver, port, client_socket, request):
        # Function to proxy HTTP traffic.
        # Connect to the web server,
        # forward the request,
        # and relay the response.
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((webserver, port))
        server_socket.send(request)

        while True:
            data = server_socket.recv(CHUNK_SIZE_L)
            if len(data) > NUMBER_ZERO:
                client_socket.send(data)
            else:
                break

    def proxy_https(self, host, port, client_socket):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(
                (host, int(port)))  # Ensure port is an integer
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            def forward_traffic(src, dst):
                while True:
                    try:
                        data = src.recv(CHUNK_SIZE_L)
                        if len(data) > 0:
                            try:
                                dst.send(data)
                            except socket.error as e:
                                print(f"Error sending data: {e}")
                                break  # Break the loop if we can't send data
                        else:
                            break  # No more data to receive
                    except socket.error as e:
                        print(f"Error receiving data: {e}")
                        break  # Break the loop if there's an error
                        # receiving data

            threading.Thread(target=forward_traffic,
                             args=(client_socket, server_socket)).start()
            threading.Thread(target=forward_traffic,
                             args=(server_socket, client_socket)).start()
        except Exception as e:
            print(f"Error connecting to {host}:{port} - {str(e)}")
            client_socket.close()  # Ensure the client socket is closed on
            # error

    def start(self):
        # Function to start the proxy
        # server and handle incoming
        # client connections.
        self.initiate_login = InitiateLogin()
        self.username = self.initiate_login.get_username()
        self.banned_sites = self.initiate_login.get_banned_sites(
            self.username)
        updater_thread = threading.Thread(target=self.update_banned_sites)
        updater_thread.start()
        while True:
            client_socket, addr = self.server.accept()
            client_handler = threading.Thread(target=self.handle_client,
                                              args=(client_socket,))
            client_handler.start()


class InitiateLogin:
    def __init__(self):
        self.host = BIG_SERVER_IP_CLIENT
        self.port = BIG_SERVER_PORT

    def get_username(self):
        try:
            # Open the registry key
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                          path, NUMBER_ZERO,
                                          winreg.KEY_READ)

            # Read the registry value
            data, _ = winreg.QueryValueEx(registry_key, value_name)

            # Close the registry key
            winreg.CloseKey(registry_key)

            return data

        except Exception as e:
            print("Error: ", e)
            return None

    def get_banned_sites(self, username):
        try:
            # Create a socket connection to bigServer
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))

                # Send the username to bigServer
                data = {'action': 'get_banned_sites', 'username': username}
                serialized_data = pickle.dumps(data)
                # s.sendall(serialized_data)
                Protocol.send_bin(s, serialized_data)

                # Receive the response from bigServer
                response_data = Protocol.recv(s)
                # response_data = s.recv(CHUNK_SIZE_L)
                banned_sites = pickle.loads(response_data)

                return banned_sites

        except Exception as e:
            print("Error: ", e)
            return None


def check_wifi_connected():
    command = "netsh wlan show interfaces"
    while True:
        try:
            output = subprocess.check_output(command, shell=True, universal_newlines=True)
            # Split the output into lines for more accurate analysis
            lines = output.split('\n')
            # Find the line containing the connection state
            connected_line = [line for line in lines if "State" in line and "disconnected" not in line.lower()]
            if connected_line and "connected" in connected_line[0].lower():
                print("Connected to WiFi.")
                break
            else:
                print("Not connected to WiFi. Checking again...")
        except subprocess.CalledProcessError as e:
            print(f"Failed to check WiFi status: {e}")
        time.sleep(5)


def main():
    # Check if the computer is connected to Wi-Fi,
    # only proceed if connected
    check_wifi_connected()
    # Create an instance of the ProxyServer class and start the proxy server.
    login_data = InitiateLogin()
    username = login_data.get_username()
    banned_sites = login_data.get_banned_sites(username)
    proxy = ProxyServer(IP, SERVER_PORT, banned_sites)
    proxy.start()
    threading.Thread(target=proxy.clear_banned_times).start()


if __name__ == '__main__':
    main()
