from functools import partial
from Scripts.parser import create_parse_args
from Scripts.conf import Configuration
from Scripts.bd_client import RedisClient
from Scripts.logger import logger_init
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import random


class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, bd, *args, **kwargs):
        self._bd = bd
        self._host = f"http://{conf.server_http.ip}:{conf.server_http.port}"
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
            logger.info(f"Redirect to {self._host + long_url}")
            self._set_headers(301, 'Location', self._host + long_url)

    def do_POST(self):
        logger.info(f"POST request from: {self.client_address}")
        logger.debug(f"request: {self.request}")
        short_url = "/" + base64.b64encode(random.randbytes(6), altchars=None).decode()
        self._bd.set(short_url, self.path, conf.db.url_ttl)
        self._set_headers(200, 'Content-type', 'text/html')
        logger.info(f"Response to POST request: {self._host + short_url}")
        self.wfile.write((self._host + short_url).encode())


if __name__ == '__main__':
    args = create_parse_args().parse_args()
    if args.command is None:
        logger = logger_init("run")
    else:
        logger = logger_init("run", args.level, args.path)
    logger.info("Start")
    logger.debug(f"Launch parameters: {args}")
    logger.info(f"Loading configuration from file {args.configuration.name}")
    conf = Configuration.load_json(args.configuration.name)
    logger.info(f"Loading configuration complete")
    logger.debug(f"Configuration: {conf}")
    with RedisClient(host=conf.db.ip) as db_client:
        custom_handler = partial(MyHandler, db_client)
        server = ThreadingHTTPServer((conf.server_http.ip, conf.server_http.port), custom_handler)
        logger.info(f"Started HTTP server {conf.server_http.ip} on port: {conf.server_http.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Stop HTTP server")
            server.shutdown()
