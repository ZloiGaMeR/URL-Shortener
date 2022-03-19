from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MyHandler(BaseHTTPRequestHandler):
    def __init__(self,):
        super().__init__()


    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.path

    def do_POST(self):
        pass


if __name__ == '__main__':
    port = 8080
    server = ThreadingHTTPServer(('127.0.0.1', port), MyHandler)
    print('Started HTTP server on port: {}'.format(port))
    # бесконечно ожидаем входящие http запросы
    server.serve_forever()
