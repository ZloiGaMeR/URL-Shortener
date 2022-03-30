import base64
import logging
import random
import re
from http.server import BaseHTTPRequestHandler

regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

logger = logging.getLogger('url_shortener.server')


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

    def do_GET(self):
        logger.info(f"GET request from: {self.client_address}")
        logger.debug(f"request: {self.request}")
        long_url = self._bd.get(self.path.encode())
        if long_url is None:
            self.send_error(404)
            logger.info("404 error")
        else:
            logger.info(f"Redirect to {long_url}")
            self._set_headers(301, 'Location', long_url)

    def do_POST(self):
        logger.info(f"POST request from: {self.client_address}")
        if self.headers['content-type'] == 'application/x-www-form-urlencoded':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            if re.match(regex, post_data):
                logger.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                             str(self.path), str(self.headers), post_data)
                short_url = "/" + base64.b64encode(random.randbytes(6), altchars=None).decode()
                self._bd.set(short_url, post_data, self._ttl)
                self._set_headers(200, 'Content-type', 'text/html')
                logger.info(f"Response to POST request: 'Your short URL: {self._host + short_url}'")
                self.wfile.write(f"Your short URL: {self._host + short_url}".encode())
            else:
                self._set_headers(200, 'Content-type', 'text/html')
                logger.info(f"Response to POST request: URL {post_data} is not correct")
                self.wfile.write(f"URL {post_data} is not correct.".encode())
        else:
            self._set_headers(200, 'Content-type', 'text/html')
            logger.info(f"Response to POST request: ")
            self.wfile.write("Not correct POST request. Supported requests like: "
                             "curl -X POST -d "'https://github.com/ZloiGaMeR/URL-Shortener'" 127.0.0.1:8080 ".encode())
