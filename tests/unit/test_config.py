"""Tests for config.py"""
import fileinput
import logging.config
import os
import re
import shutil
import stat
import sys
import tempfile

import pytest

import aviacme.config

ORG_CWD = os.getcwd()


def setup_module(module):
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    for folder in aviacme.config.CONFIG_DIRS:
        os.makedirs(folder)


def teardown_module(module):
    if "/tmp/" in os.getcwd():
        shutil.rmtree(os.getcwd())
    os.chdir(ORG_CWD)


def test_check_configfiles():
    assert not aviacme.config.check_configfiles()
    with open(aviacme.config.CONFIG_FILE, "a") as open_file:
        open_file.write("hei")
    with open(aviacme.config.LOG_CONFIG_FILE, "a") as open_file:
        open_file.write("hei")
    assert aviacme.config.check_configfiles()
    os.rmdir("cert/backup")
    assert not aviacme.config.check_configfiles()
    os.remove(aviacme.config.CONFIG_FILE)
    os.remove(aviacme.config.LOG_CONFIG_FILE)


def test_create_and_read_configfile():

    # the config file should not be world readable, even with an permissive umask
    os.umask(0o0000)
    aviacme.config.create_configfile()
    assert oct(os.stat(aviacme.config.CONFIG_FILE)[stat.ST_MODE]) == "0o100660"

    config = aviacme.config.read_configfile()

    # the host 2 option should not be used if Cluster = False
    for line in fileinput.input(str(aviacme.config.CONFIG_FILE), inplace=True):
        sys.stdout.write(
            re.sub("cluster = (True|False)", "cluster = False", line).replace(
                "host 2 = lb2.example.com", ""
            )
        )
    config = aviacme.config.read_configfile()
    assert config.lb2 is None

    # If use proxy = True, the proxy address should be read
    for line in fileinput.input(str(aviacme.config.CONFIG_FILE), inplace=True):
        sys.stdout.write(re.sub("use proxy = (True|False)", "use proxy = True", line))
    config = aviacme.config.read_configfile()
    assert config.ca_proxy == "http://proxy.example.com:8080"

    # The proxy address should not be used if use proxy = False
    for line in fileinput.input(str(aviacme.config.CONFIG_FILE), inplace=True):
        sys.stdout.write(
            re.sub("use proxy = (True|False)", "use proxy = False", line).replace(
                "proxy = http://proxy.example.com:8080", ""
            )
        )
    config = aviacme.config.read_configfile()
    assert not config.ca_proxy

    # The plugin config should be False by default
    assert not config.plugin

    # If there is a Plugin section, the whole should be returned as config.plugin
    plugin_config = "[Plugin]\noption1 = yes\noption2 = no"
    with open(aviacme.config.CONFIG_FILE, "a") as config_file:
        config_file.write(plugin_config)
    config = aviacme.config.read_configfile()
    assert len(config.plugin) == 2
    assert config.plugin[0][1] == "yes"
    assert config.plugin[1][1] == "no"


def test_create_logconfigfile():
    """ Creates a normal logconfig file"""
    aviacme.config.create_logconfigfile(False)
    logging.config.fileConfig(aviacme.config.LOG_CONFIG_FILE)
    # root logger should be INFO and the bigacme logger nothin, but should propagate
    assert logging.getLogger().level == 20
    assert logging.getLogger("bigacme").level == 0
    assert logging.getLogger("bigacme").propagate == 1


def test_create_logconfigfile_debug():
    """ Creates a debug logconfig file"""
    aviacme.config.create_logconfigfile(True)
    logging.config.fileConfig(aviacme.config.LOG_CONFIG_FILE)
    # root logger should be INFO and the bigacme logger DEBUG and not propagate
    assert logging.getLogger().level == 20
    assert logging.getLogger("bigacme").level == 10
    assert logging.getLogger("bigacme").propagate == 0
