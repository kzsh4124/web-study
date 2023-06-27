import socket
from henango.server.worker import Worker

class Server:

    def serve(self):
        print("=== Server: boot server ===")

        try:
            # create socket
            server_socket = self.create_server_socket()
            
            while True:
                # accept connections
                print("=== Server: Wating for client ===")
                (client_socket, address) = server_socket.accept()
                print(f"=== Server: Client Established! The address is {address} ===")
                
                # Create a new thread
                thread = Worker(client_socket, address)
                # run the thread
                thread.start()

        finally:
            print("=== server stopped ===")
            
    def create_server_socket(self) -> socket.socket:
            # create socket
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # bind the socket to a port
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)
            return server_socket
    
