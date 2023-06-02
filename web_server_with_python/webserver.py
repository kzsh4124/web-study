import socket
from datetime import datetime
import os
import traceback
from typing import Tuple

class WebServer:
    # dir definition
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    # MIME Type
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    def serve(self):
        print("boot server")

        try:
            # create socket
            server_socket = self.create_server_socket()
            
            while True:
                # accept connections
                print("=== Wating for client ===")
                (client_socket, address) = server_socket.accept()
                print(f"=== Client Established! The address is {address} ===")
                
                try:
                    self.handle_client(client_socket)
                except Exception:
                    print("=== error occurred ===")
                    traceback.print_exc()
                finally:
                    # close the connection
                    client_socket.close()

        finally:
            print("=== server stopped ===")
            
    def create_server_socket(self) -> socket:
                    # create socket
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # bind the socket to a port
            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)
            return server_socket
    
    def handle_client(self, client_socket: socket) -> None:
        print("=== client start ===")
        # get the request
        request = client_socket.recv(4096)
        # save the request
        with open("server_recv.txt", "wb") as f:
            f.write(request)
        
        # parse the request
        method, path, http_version, request_header, request_body = self.parse_http_request(request)
        print("requested path: ",path)
        
        try:
            # response body
            response_body = self.get_static_file_content(path)
            # response line
            response_line = "HTTP/1.1 200 OK\r\n"
            # relative path
            relative_path = path.lstrip("/")
            # html path
            static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
            
            # create response body & response line
            with open(static_file_path, "rb") as f:
                response_body = f.read()
                response_line = "HTTP/1.1 200 OK\r\n"
        except OSError:
            response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
            response_line = "HTTP/1.1 404 Not Found\r\n"

        # create response header
        response_header = self.build_response_header(path, request_body, response_line)
        # response
        response = (response_line + response_header + "\r\n" ).encode() + response_body
        client_socket.send(response)


    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
        """
        returns
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: bytes
        5. request_body: bytes
        """
        print("=== parse start ===")
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)
        # parse the request line (string)
        method, path, http_version = request_line.decode().split(" ")
        return method, path, http_version, request_header, request_body
    
    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()
    

    def build_response_header(self, path: str, response_body: bytes, response_line) -> str:
        print("===start building response===")
        """
        レスポンスヘッダーを構築する
        """
        # ヘッダー生成のためにContent-Typeを取得しておく
        # pathから拡張子を取得
        if "." in path:
            ext = path.rsplit(".", maxsplit=1)[-1]
        else:
            ext = ""
        # 拡張子からMIME Typeを取得
        # 知らない対応していない拡張子の場合はoctet-streamとする
        # 404なときはtext/htmlにする
        if response_line == "HTTP/1.1 200 OK\r\n":
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
        else:
            content_type = "text/html"

        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header

if __name__ == "__main__":
    server = WebServer()
    server.serve()