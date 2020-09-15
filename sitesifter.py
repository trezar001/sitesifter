import requests
import sys
import os
import argparse
from colorama import Fore
from tabulate import tabulate

#make file from any directory
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
pwd = os.popen('pwd').read().strip('\n')

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--domains', type=str, metavar='', required=True, help='text file containing list of domains to use')
parser.add_argument('-D', '--directory', type=str, metavar='', default=pwd+'/output', help='specify path to directory for outfiles')

parser.add_argument('-p', '--port', type=str, metavar='', default=8080, help='Specify port for local proxy')      
parser.add_argument('-t', '--timeout', type=int, metavar='', default=1, help="Timeout in seconds to wait for response") 

noise = parser.add_mutually_exclusive_group()
noise.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity')
noise.add_argument('-q', '--quiet', action='store_true', help='Decrease verbosity')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
   
outputdir = args.directory
contacted = []
lost = []
codes = {}

options = []

options.append(["Domain File", pwd+'/'+args.domains])
options.append(["Timeout", str(args.timeout) + ' second(s)'])
options.append(["Proxy", 'http://127.0.0.1:' + str(args.port)])
options.append(["Output Directory", args.directory])
options.append(["Verbose", args.verbose])

print(Fore.LIGHTBLUE_EX + '\n[?] Options:')
print(Fore.LIGHTBLUE_EX + tabulate(options, tablefmt='pretty',colalign=("left",)))

try:
    with open(args.domains, 'r') as f:

        size = os.popen('wc -l ' + args.domains + ' | cut -d " " -f 1').read().strip('\n')
        print(Fore.YELLOW + '\n[*] File ' + args.domains + ' containing ' + str(size) + ' domain(s) being tested\n')

        for line in f:
            domain = line.strip('\n')

            http = 'http://' + domain

            proxy = { "http" : 'http://127.0.0.1:'+str(args.port)
                    }

            try:
                r = requests.get(http, proxies=proxy, verify=False, timeout=args.timeout)
                contacted.append(domain + ': ' + str(r.status_code))

                if(args.verbose):
                    print(Fore.GREEN + '[+] ' + str(r.status_code) + ' status code for: ' + domain)
                else:
                    print(Fore.GREEN + '[+] ' + domain)
                    
            except:
                if(args.verbose):
                    print(Fore.RED + '[-] timeout for domain: ' + domain)
                lost.append(domain) 
except:
    print(Fore.RED + '[-] File can not be found!')
    sys.exit(1)

try:
    os.mkdir(outputdir)
except:
    print(Fore.RED + '\n[-] Error creating directory \'' + outputdir +'\'! Does the directory already exist?')

if(args.verbose):
    print(Fore.YELLOW +  '\n[*] Creating files \'reachable-domains.txt\' and \'unreachable-domains.txt\'')

try:
    with open('output/reachable.txt', 'w') as f:
        for entry in contacted:
            code = entry.split(" ")[1]
            if code not in codes:
                codes.update({code:[entry]})
            else:
                codes[code].append(entry)

            f.write(entry + '\n')

    with open('output/unreachable.txt', 'w') as f:
        for entry in lost:
            f.write(entry + '\n')

    for key in codes:
        if(args.verbose):
            print(Fore.YELLOW + '[*] ' + str(len(codes[key])) + ' domains found with status code ' + str(key) + ' written to file \'' + key + '-domains.txt\'')
        with open('output/' + key + '-domains.txt', 'w') as f:
            for entry in codes[key]:
                f.write(entry + '\n')
except:
    print(Fore.RED + '\n[-] Error writing files to directory \'' + outputdir +'\'! Check permissions.')
    print(Fore.RED + '\n[-] Failure to write output. Exiting program.')
    sys.exit(1)

print(Fore.YELLOW + '\n[*] results written to directory ' + outputdir + '\n')