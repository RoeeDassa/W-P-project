"""
Edan Jacobson
Protocols for client - methods to send and receive
"""
import client_constants


class Protocol(object):
    @staticmethod
    def send(socket, data):
        """
        Method that receives socket and data and sends it to socket
        :param socket:
        :param data:
        """
        byte_value = str(len(data.encode())).zfill(
            client_constants.BYTE_SIZE).encode()
        socket.send(byte_value + data.encode())

    @staticmethod
    def send_bin(socket, data):
        """
        Method that receives socket and data and sends it to socket
        :param socket:
        :param data:
        """
        byte_value = str(len(data)).zfill(client_constants.BYTE_SIZE).encode()
        socket.send(byte_value + data)

    @staticmethod
    def recv(socket):
        """
        Method that receives socket and receives the data incoming
        :param socket:
        """
        code_size_len = client_constants.READ_SIZE
        total_data = b''

        while code_size_len:
            data = socket.recv(code_size_len)
            code_size_len -= len(data)
            total_data += data

        size = int(total_data.decode())
        total_data = b''
        while size:
            data = socket.recv(size)
            size -= len(data)
            total_data += data

        return total_data
