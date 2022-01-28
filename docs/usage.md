Usage
===

To get a certificate:

1) Generate a CSR
 Template -> Security -> SSL/TLS Certificates -> Create->Application Certificate. Fill in a name and set type to CSR, then fill in the Common Name and Subject Alternate Names - A sane minimum is including the CN as a SAN.

2) Run aviacme
 While in the configuration folder, run ```aviacme new tenant csrname --dns```. So if you called the csr "example.com_LetsEncrypt" and it is located in the app01 tenant, run ```aviacme new app01 example.com_LetsEncrypt --dns```.

Now you're done. The certificate will be installed on AVI and renewed before it expires.
