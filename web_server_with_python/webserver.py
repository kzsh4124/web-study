import socket
from datetime import datetime
import os

class WebServer:
    # dir definition
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

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
            
            # parse the request
            request_line, remain = request.split(b"\r\n", maxsplit=1)
            request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)
            
            # parse the request line
            method, path, http_version = request_line.decode().split(" ")
            # relative path
            relative_path = path.lstrip("/")
            # html path
            static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
            
            # create response body & response line
            try:
                with open(static_file_path, "rb") as f:
                    response_body = f.read()
                    response_line = "HTTP/1.1 200 OK\r\n"
            except OSError:
                response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                response_line = "HTTP/1.1 404 Not Found\r\n"
            
            
            # create response header
            response_header = ""
            response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: HenaServer/0.1\r\n"
            response_header += f"Content-Length: {len(response_body)}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"
            
            # response
            response = (response_line + response_header + "\r\n" ).encode() + response_body
            
            connected_socket.send(response)

            # close the connection
            connected_socket.close()
        
        finally:
            print("=== server stopped ===")

if __name__ == "__main__":
    server = WebServer()
    server.serve()