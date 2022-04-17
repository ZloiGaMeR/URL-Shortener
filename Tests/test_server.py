import pytest
import sys
import redis
import mock
from io import BytesIO as IO

sys.path.append(r"E:\GIT_Python\URL-Shortener\scripts")
from scripts.server import MyHandler
from scripts.bd_client import DBClient


class TestServerSuite:

    @classmethod
    def setup_class(cls):
        print('Before test suite')
        redis.StrictRedis = mock.Mock()
        cls.db = DBClient()
        cls.db._r.get.side_effect = [b"1", None]

    @classmethod
    def teardown_class(cls):
        print('After test suite')

    def test_do_post(self):
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        MyHandler.wfile = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: application/x-www-form-urlencoded\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'URL 123 is not correct.')
        handler.rfile.read = mock.Mock()
        handler.rfile.read.return_value = b"https://habr.com/ru/all/"
        handler.gen_url = mock.Mock()
        handler.gen_url.return_value = "abcdefg"
        handler.do_POST()
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'Your short URL: http://127.0.0.1:6379/abcdefg')
        assert handler._bd._r.set.call_count == 1
        assert handler.rfile.read.return_value.decode() == handler._bd._r.set.call_args.args[1]
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: text/html\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'Not correct POST request. Supported requests like: '
                                                       b'curl -X POST -d https://github.com/ZloiGaMeR/URL-Shortener '
                                                       b'127.0.0.1:8080 ')

    def test_do_get(self):
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"GET /https://habr.com/ru/all/ HTTP/1.1\n")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(301)
        handler.do_GET()
        handler.send_error.assert_called_with(404)
        assert handler._bd._r.get.call_count == 2


if __name__ == '__main__':
    pytest.main()
