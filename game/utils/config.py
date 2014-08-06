import os
import logging


logging.basicConfig(
    format="%(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
)


class Config:
    def __getattr__(self, item):
        return os.environ[item.upper()]


config = Config()
