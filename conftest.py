import os
import subprocess

import pytest

from aviacme import config


def pytest_addoption(parser):
    parser.addoption(
        "--lb",
        action="store",
        default="localhost",
        help="AVI hostname or IP address",
    )
    parser.addoption("--user", action="store", help="AVI username", default="admin")
    parser.addoption("--pass", action="store", help="AVI password", default="admin")
    parser.addoption(
        "--ca", action="store", help="ACME CA directory", default="localhost"
    )
    parser.addoption(
        "--hostname",
        action="store",
        help="Hostname to retrive certificate for",
        default="aviacme.no",
    )
    parser.addoption(
        "--tenant",
        action="store",
        help="Tenant for certificate",
        default="admin",
    )
    parser.addoption(
        "--system-user",
        action="store",
        help="System user to use "
        "(tests must be run as root for this to have an effect)",
        default="aviacme",
    )


@pytest.fixture(scope="module")
def opt_lb(request):
    return request.config.getoption("--lb")


@pytest.fixture(scope="module")
def opt_username(request):
    return request.config.getoption("--user")


@pytest.fixture(scope="module")
def opt_password(request):
    return request.config.getoption("--pass")


@pytest.fixture(scope="module")
def opt_ca(request):
    return request.config.getoption("--ca")


@pytest.fixture(scope="module")
def opt_hostname(request):
    return request.config.getoption("--hostname")


@pytest.fixture(scope="module")
def opt_tenant(request):
    return request.config.getoption("--tenant")


@pytest.fixture(scope="module")
def opt_user(request):
    return request.config.getoption("--system-user")


# pebble is module scoped even though it is used by several
# modules, so that it is always killed by the same user as it
# was created (the user is changed in the unit tests for cert.py
# if the tests are run as root)
@pytest.fixture(scope="module")
def pebble():
    # Pebble reject 15 % of nonces by default,
    # turn that off to get reliable testing.
    # (clients should handle that gracefully,
    # and python-acme will retry requests
    # once in case of bad nonce, but Pebble
    # will sometimes reject two requsts in a
    # row, so the tests sometimes fails anyways).
    env = {"PEBBLE_WFE_NONCEREJECT": "0"}

    pebble_proc = subprocess.Popen(
        [
            "tests/functional/pebble/pebble",
            "-config",
            "tests/functional/pebble/pebble-config.json",
        ],
        stdout=subprocess.PIPE,
        env=env,
    )

    while b"Root CA certificate available at" not in pebble_proc.stdout.readline():
        pebble_proc.poll()
        if pebble_proc.returncode is not None:
            raise Exception("Pebble failed to start")
    yield pebble_proc
    pebble_proc.kill()
    # for easier debugging
    print(pebble_proc.communicate()[0].decode())
