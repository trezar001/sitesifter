# sitesifter
## Description
Short python script to sift through a list of domains and send GET requests while reporting their status codes. This tool has the ability to work with a proxy such as burp in order to automatically add these domains to the site map or perform other functionality.

## Usage
```
usage: sitesifter.py [-h] -d  [-D] [-t] [-p  | --no-proxy] [-v | -q]

optional arguments:
  -h, --help         show this help message and exit
  -d , --domains     text file containing list of domains to use
  -D , --directory   specify path to directory for outfiles
  -t , --timeout     timeout in seconds to wait for response
  -p , --port        specify port for local proxy
  --no-proxy         disable usage of a proxy
  -v, --verbose      increase verbosity
  -q, --quiet        decrease verbosity
```
