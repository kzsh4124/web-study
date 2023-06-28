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
import views
from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse

import settings
from henango.urls.resolver import URLResolver

class Worker(Thread):
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

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        302: "302 Found",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]) -> None:
        super().__init__()
        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        try:
            # get the request
            request_bytes = self.client_socket.recv(4096)
            # save the request
            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)
            
            # parse the request
            request = self.parse_http_request(request_bytes)
            
            
            
            # URL解決
            view = URLResolver().resolve(request)

            # レスポンスを取得する
            response = view(request)
            
            # レスポンスボディを変換
            if isinstance(response.body, str):
                response.body = response.body.encode()

            


            # レスポンスラインを生成
            response_line = self.build_response_line(response)
            # create response header
            response_header = self.build_response_header(response, request)
            # response
            response = (response_line + response_header + "\r\n" ).encode() + response.body
            self.client_socket.send(response)
            
        except Exception:
            print("=== Worker: error occurred ===")
            traceback.print_exc()
        finally:
            print(f"=== Worker: close connection with client. remote address: {self.client_address} ===")
            self.client_socket.close()


    def parse_http_request(self, request: bytes) -> HTTPRequest:
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
            
        
        cookies = {}
        if "Cookie" in headers:
            # str から list へ変換 (ex) "name1=value1; name2=value2" => ["name1=value1", "name2=value2"]
            cookie_strings = headers["Cookie"].split("; ")
            # list から dict へ変換 (ex) ["name1=value1", "name2=value2"] => {"name1": "value1", "name2": "value2"}
            for cookie_string in cookie_strings:
                name, value = cookie_string.split("=", maxsplit=1)
                cookies[name] = value
        
        # 機能追加: ルートをindex.htmlに飛ばす
        if path == '/':
            path = '/index.html'
        
        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, body=request_body, cookies=cookies)
    

    
    def build_response_line(self, response: HTTPResponse) -> str:
        """
        レスポンスラインを構築する
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}\r\n"

    def build_response_header(self, response: HTTPResponse, request: HTTPRequest ) -> str:
        """
        レスポンスヘッダーを構築する
        """
        # ヘッダー生成のためにContent-Typeを取得しておく
        # pathから拡張子を取得
        if response.content_type is None:
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            response.content_type = "text/html; charset=UTF-8"
            # 追加機能: 404なときはtext/htmlにする


        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"
        
        for header_name, header_value in response.headers.items():
            response_header += f"{header_name}: {header_value}\r\n"
        
        # Cookieヘッダーの生成
        for cookie in response.cookies:
            cookie_header = f"Set-Cookie: {cookie.name}={cookie.value}"
            if cookie.expires is not None:
                cookie_header += f"; Expires={cookie.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            if cookie.max_age is not None:
                cookie_header += f"; Max-Age={cookie.max_age}"
            if cookie.domain:
                cookie_header += f"; Domain={cookie.domain}"
            if cookie.path:
                cookie_header += f"; Path={cookie.path}"
            if cookie.secure:
                cookie_header += "; Secure"
            if cookie.http_only:
                cookie_header += "; HttpOnly"

            response_header += cookie_header + "\r\n"

        return response_header
