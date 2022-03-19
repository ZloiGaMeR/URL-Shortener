from functools import partial
from Scripts.conf import Configuration
from Scripts.bd_client import RedisClient
from Scripts.logger import Logger
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import random
import argparse


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
        long_url = self._bd.get(self.path.encode())
        if long_url is None:
            self.send_error(404)
        else:
            self._set_headers(301, 'Location', self._host + long_url)

    def do_POST(self):
        short_url = "/" + base64.b64encode(random.randbytes(6), altchars=None).decode()
        self._bd.set(short_url, self.path, conf.db.url_ttl)
        self._set_headers(200, 'Content-type', 'text/html')
        self.wfile.write((self._host + short_url).encode())


def parse_args():
    parser = argparse.ArgumentParser(description='Simple URL shortener')
    parser.add_argument('-c', '--configuration', help='Path to configuration file')
    return parser.parse_args()


if __name__ == '__main__':
    conf_path = r"E:\GIT_Python\URL Shortener\Conf\config.json"
    conf = Configuration.load_json(conf_path)
    # args = parse_args()
    # conf = Configuration.load_json(args.configuration)
    logger = Logger(conf, __name__).get_logger()
    print(logger.level)
    logger.info("test")
    logger.info("Program started")
    with RedisClient(host=conf.db.ip) as db_client:
        custom_handler = partial(MyHandler, db_client)
        server = ThreadingHTTPServer((conf.server_http.ip, conf.server_http.port), custom_handler)
        print('Started HTTP server on port: {}'.format(conf.server_http.port))
        # бесконечно ожидаем входящие http запросы
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
