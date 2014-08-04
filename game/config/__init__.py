import tornado.options
import logging
import os

# can be optionally created, is ignored in VCS
CONFIG_LOCAL = "settings_local.py"

# default config file, settings from this file may be overwritten in local config file
# or in config file specified from command line
CONFIG_DEFAULT = "settings.py"

logger = logging.getLogger(__file__)


def parse_config_file(config_file):
    #parse default options
    path = os.path.dirname(__file__)
    config_path = os.path.join(path, CONFIG_DEFAULT)
    logger.info("parsing options from default config file: %s", config_path)
    tornado.options.parse_config_file(config_path)

    if config_file:
        #parse specified config file that overwrites default settings
        logger.info("parsing options from config file: %s", config_file)
        tornado.options.parse_config_file(config_file)
        return
    try:
        #config file was not specified try to load local config
        config_path = os.path.join(path, CONFIG_LOCAL)
        logger.info("parsing options from config file: %s", config_path)
        tornado.options.parse_config_file(config_path)
    except IOError:
        logger.warning("""
cannot find local config file: %s, create one basing on config_local_example.py
starting with default options""", config_path)


def configure(config_path=None, already_loaded=[]):
    """loads default and user defined config options, subsequent calls are ignored"""
    if already_loaded and not config_path:
        return
    if not already_loaded:
        already_loaded.append(True)

        tornado.options.define("config", help="config file", type=str)
        tornado.options.define("port", help="server port", default=5000, type=int)
        tornado.options.define("address", help="server address", default="127.0.0.1", type=str)

        #configure logging
        logging.basicConfig(
            format="%(levelname)s:%(name)s: %(message)s",
            level=logging.DEBUG,
        )

        #setup django settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.config.django_settings")

    if not config_path:
        #tornado.options.parse_command_line()
        config_path = tornado.options.options.config
    parse_config_file(config_path)
