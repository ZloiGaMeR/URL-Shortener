from functools import partial
from http.server import ThreadingHTTPServer

from scripts.conf import Configuration
from scripts.db_client import DBClient, TimeoutException
from scripts.logger import logger_init
from scripts.parser import create_parse_args
from scripts.server import MyHandler

if __name__ == '__main__':
    args = create_parse_args().parse_args()
    if args.command is None:
        logger = logger_init("url_shortener")
    else:
        logger = logger_init("url_shortener", args.level, args.path)
    logger.info("Start")
    logger.debug(f"Launch parameters: {args}")
    logger.info(f"Loading configuration from file {args.configuration.name}")
    conf = Configuration.load_json(args.configuration.name)
    logger.info(f"Loading configuration complete")
    logger.debug(f"Configuration: {conf}")
    try:
        with DBClient(host=conf.db.ip, port=conf.db.port, db=conf.db.index,
                      charset=conf.db.charset, decode_responses=conf.db.decode_responses) as db_client:
            custom_handler = partial(MyHandler, db_client, conf.server_http.ip, conf.server_http.port, conf.db.url_ttl)
            server = ThreadingHTTPServer((conf.server_http.ip, conf.server_http.port), custom_handler)
            logger.info(f"Started HTTP server {conf.server_http.ip} on port: {conf.server_http.port}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                logger.info("Stop HTTP server")
                server.shutdown()
    except TimeoutException:
        logger.critical("Exit application")
        raise SystemExit
