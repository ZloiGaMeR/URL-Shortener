import base64
import logging
import random
import re
from http.server import BaseHTTPRequestHandler

_regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

_logger = logging.getLogger('url_shortener.server')

INCORRECT_REQUEST = "Not correct POST request. Supported requests like: " \
                    "curl -X POST -d "'https://github.com/ZloiGaMeR/URL-Shortener'" 127.0.0.1:8080 "


class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, bd, ip, port, ttl, *args, **kwargs):
        self._bd = bd
        self._ip = ip
        self._port = port
        self._ttl = ttl
        self._host = f"http://{self._ip}:{self._port}"
        super().__init__(*args, **kwargs)

    def _set_headers(self, response, keyword, value):
        self.send_response(response)
        self.send_header(keyword, value)
        self.end_headers()

    @staticmethod
    def gen_url(length):
        return base64.b64encode(random.randbytes(length), altchars=None).decode()

    def do_GET(self):
        _logger.info(f"GET request from: {self.client_address}")
        _logger.debug(f"request: {self.request}")
        long_url = self._bd.get(self.path.encode())
        if long_url is None:
            self.send_error(404)
            _logger.info("404 error")
        else:
            _logger.info(f"Redirect to {long_url}")
            self._set_headers(301, 'Location', long_url)

    def do_POST(self):
        _logger.info(f"POST request from: {self.client_address}")
        if self.headers['content-type'] == 'application/x-www-form-urlencoded':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            if re.match(_regex, post_data):
                _logger.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                              str(self.path), str(self.headers), post_data)
                short_url = "/" + self.gen_url(6)
                self._bd.set(short_url, post_data, self._ttl)
                self._set_headers(200, 'Content-type', 'text/html')
                _logger.info(f"Response to POST request: 'Your short URL: {self._host + short_url}'")
                self.wfile.write(f"Your short URL: {self._host + short_url}".encode())
            else:
                self._set_headers(200, 'Content-type', 'text/html')
                _logger.info(f"Response to POST request: URL {post_data} is not correct")
                self.wfile.write(f"URL {post_data} is not correct.".encode())
        else:
            self._set_headers(200, 'Content-type', 'text/html')
            _logger.info(f"Response to POST request: ")
            self.wfile.write(INCORRECT_REQUEST.encode())
