import socket

class TCPServer:
    def serve(self):
        print("boot server")

        try:
            # create socket
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # bind the socket to a port
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)
            
            # accept connections
            print("=== Wating for client ===")
            (connected_socket, address) = server_socket.accept()
            print(f"=== Client Established! The address is {address} ===")
            
            # get the request
            request = connected_socket.recv(4096)
            
            # save the data
            with open("server_recv.txt", "wb") as f:
                f.write(request)
                
            # send the response
            with open("server_send.txt", "rb") as f:
                response = f.read()
            
            connected_socket.send(response)

            # close the connection
            connected_socket.close()
        
        finally:
            print("=== server stopped ===")

if __name__ == "__main__":
    server = TCPServer()
    server.serve()