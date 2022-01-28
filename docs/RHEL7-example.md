# Example installation on RHEL 7

This is an example of how you can install aviacme on RHEL 7, and use the setup with several AVI.

## Prerequisites

Python in RHEL 7 does not do certificate validation by default. This is bad, and must be changed. It is configured in the file */etc/python/cert-verification.cfg*.

Change from:

```
[https]
verify=platform_default
```
to:
```
[https]
verify=enable
```

After this, the CA that issued the certificates for AVI must be trusted (add it to /etc/pki/ca-trust/source/anchors and run update-ca-trust).

Then install some extra needed packages:

`# yum install python-virtualenv libffi-devel gcc git openssl-devel`

As RHEL 7 does not have Python 3.6 by default, you'll also need to install it. It can be installed from EPEL, RHSCL or manually.

Add a user for aviacme:

`# useradd aviacme`

Create configuration folders:

```
# mkdir -p /opt/aviacme/venvs /opt/aviacme/configs
# chown aviacme:aviacme /opt/aviacme -R
```

Users that should have the privilege to issue certificate should be added to the aviacme group. The rest of this guide should be done as the aviacme user.

## Installation of virtualenv

Virtualenv is an easy way to run several individual python environments on the same server. It makes it possible to run to versions of aviacme on the same server (e.g. so that we can upgrade test before production).

Create a virtual python environment and activate it:

```
$ python36 -m venv /opt/aviacme/venvs/1
$ source /opt/aviacme/venvs/1/bin/activate
```

Upgrade pip and setuptools:

```
$ pip install --upgrade pip
$ pip install --upgrade setuptools
```

We can now install aviacme. Install the smoking fresh version from Github:

`$ pip install git+https://github.com/vidarno/aviacme.git`

## Configuration of aviacme

Now we are ready to do the configuration for aviacme. Repeat these steps for every AVI you have (e.g. dev, test, production). Here we are configuring it for a AVI we'll call "avi-test".

Create a config folder:

```
$ mkdir /opt/aviacme/configs/avi-test
$ cd /opt/aviacme/configs/avi-test
$ aviacme config
```

Change the config in config/config.ini according to your needs (see the "Configure aviacme" section in the installation doc).

Register with the CA:

`$ aviacme register`

To make it easier to activate the virtualenv we can make an alias. Add the following to /etc/profile.d/aviacme.sh

```bash
alias avi-test='if [ "$(type -t deactivate)" ]; then deactivate; fi; source /opt/aviacme/venvs/1/bin/activate; cd /opt/aviacme/configs/avi-test/; eval "$(_AVIACME_COMPLETE=source aviacme)"'
```

Now you can run "avi-test" and it will deactivate the current virtualenv (if in an virtualenv), activate the "1" virtualenv, and change directory to the configuration folder for the test box.

Then we need to add a cron job. Create this script as avi-test-cron.sh in aviacme's home folder (with execute permission):

```bash
#/bin/bash
source /etc/profile.d/aviacme.sh
avi-test
aviacme renew
```

Then add the following to the crontab for the aviacme user:

```0 12 * * * /home/aviacme/avi-test-cron.sh```

This will check for renewals every day (adjust as needed).

## Issuing certificates

Create a csr on AVI. Here we assume the csr is called "ImportantApp.no_LetsEncrypt" and it's in the tenant "ImportantApp".

Log into the server, run:

```
$ testavi
$ aviacme new ImportantApp ImportantApp.no_LetsEncrypt --dns
```

This will issue a certificate. And it will be renewed according to the config and the cron job schedule.

## Upgrading Aviacme

If you want to upgrade Aviacme, you can just create a new virtual environemt, install aviacme, and then change the path in the /etc/profile.d/aviacme.sh. You can take one AVI-instance at the time (start with dev, then test, then production), and when you have moved every instance over to the new version, you can delete the first virtual environment.
