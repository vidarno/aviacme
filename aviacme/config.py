"""Handles the configuration"""
import configparser
import logging
from collections import namedtuple
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_FILE = Path("config", "config.ini")
LOG_CONFIG_FILE = Path("config", "logging.ini")
ACCOUNT_FILE = Path("config", "account.json")
CONFIG_DIRS = [Path("config"), Path("cert"), Path("cert", "backup")]


class ConfigError(Exception):
    """Superclass for all config exceptions."""

    pass


def check_configfiles():
    """Checks that the configuration files and folders are in place"""
    return (
        all(x.is_dir() for x in CONFIG_DIRS)
        and CONFIG_FILE.is_file()
        and LOG_CONFIG_FILE.is_file()
    )


def check_account_file():
    """Checks whether the account file exists in the config folder"""
    return ACCOUNT_FILE.is_file()


def read_configfile():
    """Reads the configfile and creates a config object"""
    configtp = namedtuple(
        "Config",
        [
            "lb_user",
            "lb_pwd",
            "avi",
            "tenant",
            "ca",
            "ca_proxy",
            "cm_account",
            "cm_renewal_days",
            "cm_delayed_days",
            "plugin",
        ],
    )
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if config.getboolean("Certificate Authority", "use proxy"):
        ca_proxy = config.get("Certificate Authority", "proxy")
    else:
        ca_proxy = False

    avi = config.get("Load Balancer", "host")


    try:
        plugin_section = config.items("Plugin")
    except configparser.NoSectionError:
        plugin_section = None

    the_config = configtp(
        avi=avi,
        lb_user=config.get("Load Balancer", "username"),
        lb_pwd=config.get("Load Balancer", "password"),
        tenant=config.get("Load Balancer", "tenant"),
        ca=config.get("Certificate Authority", "directory url"),
        ca_proxy=ca_proxy,
        cm_account=config.get("Common", "account config"),
        cm_renewal_days=int(config.get("Common", "renewal days")),
        cm_delayed_days=int(config.get("Common", "delayed installation days")),
        plugin=plugin_section,
    )
    return the_config


def create_configfile():
    """Creates a default configfile"""

    account_file_path = str(Path("config", "account.json").resolve())

    config = configparser.ConfigParser()
    config.add_section("Common")
    config.set("Common", "renewal days", "40")
    config.set("Common", "delayed installation days", "5")
    config.set("Common", "account config", account_file_path)
    config.add_section("Load Balancer")
    config.set("Load Balancer", "Host", "lb1.example.com")
    config.set("Load Balancer", "username", "admin")
    config.set("Load Balancer", "password", "password01")
    config.set("Load Balancer", "tenant", "admin")
    config.add_section("Certificate Authority")
    config.set(
        "Certificate Authority",
        "Directory URL",
        "https://acme-v02.api.letsencrypt.org/directory",
    )
    config.set("Certificate Authority", "use proxy", "False")
    config.set("Certificate Authority", "proxy", "http://proxy.example.com:8080")

    # As the config file contains password,
    # we must be careful with permissions.
    CONFIG_FILE.touch(mode=0o660)

    with CONFIG_FILE.open(mode="w") as config_file:
        config.write(config_file)


def create_logconfigfile(debug):
    """
    Creates a default log config file

    Normally we just use the root logger, but if debug is specified,
    we create a separate logger for aviacme,
    and stops it from propagate to the root logger.
    Otherwise it will be flooded with suds logging

    """

    log_file_path = str(Path("log.log").resolve())

    config = configparser.ConfigParser()
    config.add_section("loggers")

    if debug:
        config.set("loggers", "keys", "root, aviacme")
    else:
        config.set("loggers", "keys", "root")

    config.add_section("handlers")
    config.set("handlers", "keys", "fileHandler")
    config.add_section("formatters")
    config.set("formatters", "keys", "fileFormatter")
    config.add_section("logger_root")
    config.set("logger_root", "level", "INFO")
    config.set("logger_root", "handlers", "fileHandler")

    if debug:
        config.add_section("logger_aviacme")
        config.set("logger_aviacme", "qualname", "aviacme")
        config.set("logger_aviacme", "level", "DEBUG")
        config.set("logger_aviacme", "handlers", "fileHandler")
        config.set("logger_aviacme", "propagate", "0")

    config.add_section("handler_fileHandler")
    config.set("handler_fileHandler", "class", "FileHandler")

    if debug:
        config.set("handler_fileHandler", "level", "DEBUG")
    else:
        config.set("handler_fileHandler", "level", "INFO")
    config.set("handler_fileHandler", "formatter", "fileFormatter")
    config.set("handler_fileHandler", "args", f"('{log_file_path}', 'a')")
    config.add_section("formatter_fileFormatter")
    config.set(
        "formatter_fileFormatter", "format", "%(asctime)s - %(levelname)s - %(message)s"
    )

    with LOG_CONFIG_FILE.open(mode="w") as config_file:
        config.write(config_file)
