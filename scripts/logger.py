import logging
import logging.config


def logger_init(name, level="INFO", filename=None):
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=filename,
                        filemode='a')
    logger = logging.getLogger(name)
    return logger
