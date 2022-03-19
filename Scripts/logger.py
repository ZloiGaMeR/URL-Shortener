import logging
import logging.config


class Logger:
    def __init__(self, config, name):
        self._name = name
        self._dictLogConfig = {
            "version": 1,
            "handlers": {
                "fileHandler": {
                    "class": "logging.FileHandler",
                    "formatter": "myFormatter",
                    "filename": config.logger.filename
                }
            },
            "loggers": {
                self._name: {
                    "handlers": ["fileHandler"],
                    "level": config.logger.level,
                }
            },
            "formatters": {
                "myFormatter": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }
        }

    def get_logger(self):
        logging.config.dictConfig(self._dictLogConfig)
        logger = logging.getLogger(self._name)
        return logger
