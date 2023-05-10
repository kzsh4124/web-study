import socket 

class TCPClient:
    def request(self):
        
        print("=== boot a client ===")
        
        try:
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # connect to server
            print("=== connecting to server ===")
            client_socket.connect(("localhost", 80))
            print("=== Established the connection! ===")
            
            with open("client_send.txt", "rb") as f:
                request = f.read()
            
            # send a request
            client_socket.send(request)
            
            # receive the response
            response = client_socket.recv(4096)
            
            # save the response
            with open("client_recv.txt", "wb") as f:
                f.write(response)

            # close the connection
            client_socket.close()
        
        finally:
            print("=== client stopped ===")
    
if __name__ == "__main__":
    client = TCPClient()
    client.request()