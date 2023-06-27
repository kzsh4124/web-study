import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.template.renderer import render

### エンドポイントに対応する関数を書いていく

def now(request: HTTPRequest) -> HTTPResponse:
    """
    現在時刻を表示するHTMLを生成する
    """
    context = {"now": datetime.now()}
    body = render("now.html", context)


    return HTTPResponse(body=body)


def show_request(request: HTTPRequest) -> HTTPResponse:

    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    context = {"request": request, "headers": pformat(request.headers), "body": request.body.decode("utf-8", "ignore")}
    body = render("show_request.html", context)

    return HTTPResponse(body=body)

def parameters(request: HTTPRequest) -> HTTPResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    if request.method == "POST":
        context = {"params": urllib.parse.parse_qs(request.body.decode())}
        body = render("parameters.html", context)
        return HTTPResponse(body=body)
    # GETリクエストの場合は、405を返す
    else:
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        return HTTPResponse(body=body, status_code=405)

 


def user_profile(request: HTTPRequest) -> HTTPResponse:
    context = {"user_id": request.params["user_id"]}

    body = render("user_profile.html", context)

    return HTTPResponse(body=body)