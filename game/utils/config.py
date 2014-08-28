import os
import logging


logging.basicConfig(
    format="%(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
)


class Config:
    def __getattr__(self, item):
        try:
            return os.environ[item.upper()]
        except KeyError:
            logging.warning("Config variable not set %s" % item)


config = Config()
