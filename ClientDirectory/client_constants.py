import socket
import os

"""
Name: constants
Author: Roee Dassa
Explanation: constants used
across all files
"""

value_name = r"UserName"
path = r"Software\CVSM"

batch_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
batch_name = r"pServerStart"
bat_file_path = r"/ClientDirectory/start_pServer.bat"
NUMBER_ZERO = 0
NUMBER_ONE = 1
NUMBER_TWO = 2
NUMBER_FIVE = 5
NUMBER_EIGHT = 8
CHUNK_SIZE_L = 4096
UTF8 = "utf-8"
GET_TYPE = "GET"
CONNECT_TYPE = "CONNECT"
CHUNK_SIZE_S = 1024
PORT_80 = 80
SERVER_PORT = 8888
# Get the hostname of the computer
hostname = socket.gethostname()
# Get the IPv4 address associated with the hostname
IP = "127.0.0.1"

html_file_path = r"/ClientDirectory/errorPage.html"
file_url = f"file://{html_file_path}"


def get_ipv4_address():
    try:
        # Create a socket object and connect
        # to an external server
        # (Google's public DNS server)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            # Get the local IP address
            ip_address = s.getsockname()[0]
        return ip_address
    except socket.error as e:
        print(f"Error occurred while getting the IPv4 address: {e}")
        return None


BIG_SERVER_IP_SERVER = "0.0.0.0"
BIG_SERVER_IP_CLIENT = "10.20.72.2"  # SET TO CURRENT SERVER COMPUTER IP
BIG_SERVER_PORT = 23456
BYTE_SIZE = 4
READ_SIZE = 4