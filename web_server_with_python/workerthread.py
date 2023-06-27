import os
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple, Optional
import textwrap
from pprint import pformat
import re
import urllib.parse

class WorkerThread(Thread):
    # dir definition
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    # MIME Type
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }
    
    def __init__(self, client_socket: socket, address: Tuple[str, int]) -> None:
        super().__init__()
        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        try:
            # get the request
            request = self.client_socket.recv(4096)
            # save the request
            with open("server_recv.txt", "wb") as f:
                f.write(request)
            
            # parse the request
            method, path, http_version, request_header, request_body = self.parse_http_request(request)
            
            response_body: bytes
            content_type: Optional[str]
            response_line: str
                        # pathが/nowのときは、現在時刻を表示するHTMLを生成する
            if path == "/now":
                html = f"""\
                    <html>
                    <body>
                        <h1>Now: {datetime.now()}</h1>
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()

                # Content-Typeを指定
                content_type = "text/html; charset=UTF-8"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"
            
            # pathが/show_requestのときは、HTTPリクエストの内容を表示するHTMLを生成する
            elif path == "/show_request":
                html = f"""\
                    <html>
                    <body>
                        <h1>Request Line:</h1>
                        <p>
                            {method} {path} {http_version}
                        </p>
                        <h1>Headers:</h1>
                        <pre>{pformat(request_header)}</pre>
                        <h1>Body:</h1>
                        <pre>{request_body.decode("utf-8", "ignore")}</pre>
                        
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()

                # Content-Typeを指定
                content_type = "text/html; charset=UTF-8"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"
            elif path == "/parameters":

                if method == "POST":
                    post_params = urllib.parse.parse_qs(request_body.decode())
                    html = f"""\
                        <html>
                        <body>
                            <h1>Parameters:</h1>
                            <pre>{pformat(post_params)}</pre>                        
                        </body>
                        </html>
                    """
                    response_body = textwrap.dedent(html).encode()

                    # Content-Typeを指定
                    content_type = "text/html; charset=UTF-8"

                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"
                
                # GETなどはこっち
                else:
                    response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"
                    response_line = "HTTP/1.1 405 Method Not Allowed\r\n"
            else:
                try:
                    # response body
                    response_body = self.get_static_file_content(path)
                    # response line
                    response_line = "HTTP/1.1 200 OK\r\n"
                    
                    content_type = None

                except OSError:
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"
                    response_line = "HTTP/1.1 404 Not Found\r\n"

            # create response header
            response_header = self.build_response_header(path, response_body, content_type)
            # response
            response = (response_line + response_header + "\r\n" ).encode() + response_body
            self.client_socket.send(response)
            
        except Exception:
            print("=== Worker: error occurred ===")
            traceback.print_exc()
        finally:
            print(f"=== Worker: close connection with client. remote address: {self.client_address} ===")
            self.client_socket.close()


    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
        """
        returns
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: bytes
        5. request_body: bytes
        """
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)
        # parse the request line (string)
        method, path, http_version = request_line.decode().split(" ")
        
        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value
        
        # 機能追加: ルートをindex.htmlに飛ばす
        if path == '/':
            path = '/index.html'
        
        return method, path, http_version, headers, request_body
    
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
    

    def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str] ) -> str:
        """
        レスポンスヘッダーを構築する
        """
        # ヘッダー生成のためにContent-Typeを取得しておく
        # pathから拡張子を取得
        if content_type is None:
            if "." in path:
                ext = path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
            # 追加機能: 404なときはtext/htmlにする


        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header
