Installation
=====

### Configure AVI

You must create a user for aviacme. It must have Write permissions to Security->SSL/TLS Certificates privilege.

### Installation of aviacme

Aviacme must be installed on a server which is able to connect to AVI and the CA. It is only tested on GNU/Linux. The easiest way is just to install it with the setup.py:

```python setup.py install```

This wil install it and all the prerequisites. Now the aviacme command is avaiable from the command line.

### Configure aviacme

Aviacme uses configuration folders to store the configuration and the certificates. You can create several configuration folders, if you have several AVI-clusters. Create a folder, run the `aviacme config` command and follow the instructions. This wil generate the needed configuration folders and config files.

Then you must adapt the config.ini file in the config folder to your environment. Most of the options should be self-explanatory, but here are the details:

```
[Common]
renewal days = This adjust how many days before the expiry date certificates will be renewed.
delayed installation days = This adjust how long to wait before installing a renewed certificate. A certificate issued seconds ago can cause troubles with some clients with bad clocks. Set to 0 for immediately installation.
account config = This is the path to the config file containing your account info (key and kid). This will be generated for you.

[Load Balancer]
host = hostname for AVI
username = Username for the account on AVI that aviacme should use.
password = Password for the account on AVI
tenant = The tenant where the datagroup resides.

[Certificate Authority]
directory url = The directory URL to the ACME CA
use proxy = Whether aviacme should use a proxy to reach the CA. True or False
proxy = The proxy to use for communcation with the CA. If you specified False above, you can delete this line.

```

When you are finished with the config.ini file, you can register with the CA with the ```aviacme register``` command. This will create an account key and register it. Follow the instructions.

Try the ```aviacme test``` command to see if everything is in order.

Now we are almost finished. But you need to add a cron job for the renewing of certificates. Add the following command to cronjob: ```aviacme --config-dir /path/to/your/config renew```. The frequency is up to you, but be aware that certs will only be renewed and installed when the cron job runs. So if you run the cron job once a week, certificates will be installed after a week, even if you specify only 2 days for "delayed installation days".

Now you are ready to get a certificate!

If you have several AVI installations, you can just set up a configuration folders and cron jobs for each one..
