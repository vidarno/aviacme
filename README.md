aviacme
=====

An ACME client for NSX Advanced Load Balancer (AVI).
It is a fork of bigacme, replacing the Big-IP support with support for AVI.

It can be used to get certificates from an ACME compatible CA, and auto-renew them before they expire. This can reduce the administrative burden of SSL.


## Prerequisites
* A server with access to both AVI and the CA
* A DNS-plugin to use with Aviacme to respond to ACME-challenges (HTTP-challenges will be supported in the future)

## How it works
You manually create a CSR on AVI and then tell aviacme to turn it into a certificate. Aviacme does so by configuring AVI to answer the challenges from the CA. When it's time to renew the certficiate, aviacme repeats the process.

See more detailed information in the docs folder.
