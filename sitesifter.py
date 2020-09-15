import requests
import sys
import os
import argparse
from colorama import Fore
from tabulate import tabulate
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#get current working directory
pwd = os.popen('pwd').read().strip('\n')

#get arguments and parse them
parser = argparse.ArgumentParser()

parser.add_argument('-d', '--domains', type=str, metavar='', required=True, help='text file containing list of domains to use')
parser.add_argument('-D', '--directory', type=str, metavar='', default=pwd+'/output', help='specify path to directory for outfiles')
parser.add_argument('-t', '--timeout', type=int, metavar='', default=1, help="timeout in seconds to wait for response") 

proxy = parser.add_mutually_exclusive_group()
proxy.add_argument('-p', '--port', type=str, metavar='', default=8080, help='specify port for local proxy')   
proxy.add_argument('--no-proxy', dest='noproxy', action='store_true', help='disable usage of a proxy')

noise = parser.add_mutually_exclusive_group()
noise.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')
noise.add_argument('-q', '--quiet', action='store_true', help='decrease verbosity')

#if no arguments provided print help message and exit
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

#initialize important variables
inputfile = os.path.abspath(args.domains)
outputdir = os.path.abspath(args.directory)
contacted = []
lost = []
codes = {}

options = []

#print options that have been selected 
options.append(["Domain File", inputfile])
options.append(["Timeout", str(args.timeout) + ' second(s)'])

if args.noproxy:
    options.append(["Proxy", 'None'])
else:
    options.append(["Proxy", 'http://127.0.0.1:' + str(args.port)])

options.append(["Output Directory", outputdir])
options.append(["Verbose", args.verbose])

#format into a nice looking table
print(Fore.LIGHTBLUE_EX + '\n[?] Options:')
print(Fore.LIGHTBLUE_EX + tabulate(options, tablefmt='pretty',colalign=("left",)))

#try to open specified file containing domains
try:
    with open(inputfile, 'r') as f:

        #if successful count the number of lines to determine the number of domains
        size = int(os.popen('wc -l ' + inputfile + ' | cut -d " " -f 1').read().strip('\n')) + 1
        print(Fore.YELLOW + '\n[*] File ' + inputfile + ' containing ' + str(size) + ' domain(s) being tested\n')

        #loop through domains
        for line in f:
            domain = line.strip('\n')
            http = 'http://' + domain

            #this proxy setting assumes that a local proxy is being used for now
            proxy = { "http" : 'http://127.0.0.1:'+str(args.port)
                    }

            #check for proxy settings
            try:
                if args.noproxy:
                    r = requests.get(http, verify=False, timeout=args.timeout)
                else:
                    r = requests.get(http, proxies=proxy, verify=False, timeout=args.timeout)

                #record data for the report
                contacted.append(domain + ': ' + str(r.status_code))

                if(args.verbose):
                    print(Fore.GREEN + '[+] ' + str(r.status_code) + ' status code for: ' + domain)
                else:
                    print(Fore.GREEN + '[+] ' + domain)
            
            #catch error if domain can't be contacted and report it
            except:
                if(args.verbose):
                    print(Fore.RED + '[-] timeout for domain: ' + domain)
                lost.append(domain) 

#file entered can't be found. exit program
except:
    print(Fore.RED + '[-] File can not be found!')
    sys.exit(1)

#make output directory if permissible to place report files
try:
    os.mkdir(outputdir)
except:
    print(Fore.RED + '\n[-] Error creating directory \'' + outputdir +'\'! Does the directory already exist?')

#create a report of all domains reached and a report of the ones we couldn't get to
if(args.verbose):
    print(Fore.YELLOW +  '\n[*] Creating files \'reachable-domains.txt\' and \'unreachable-domains.txt\'')

try:
    with open(outputdir + '/reachable.txt', 'w') as f:
        for entry in contacted:

            #snatch status code and sort entries for later 
            code = entry.split(" ")[1]
            if code not in codes:
                codes.update({code:[entry]})
            else:
                codes[code].append(entry)

            f.write(entry + '\n')

    with open(outputdir + '/unreachable.txt', 'w') as f:
        for entry in lost:
            f.write(entry + '\n')

#create reports of domains based on status codes that were returned
    for key in codes:
        if(args.verbose):
            print(Fore.YELLOW + '[*] ' + str(len(codes[key])) + ' domains found with status code ' + str(key) + ' written to file \'' + key + '-domains.txt\'')
        with open(outputdir + '/' + key + '-domains.txt', 'w') as f:
            for entry in codes[key]:
                f.write(entry + '\n')

#catch error if we can't write to specified directory
except:
    print(Fore.RED + '\n[-] Error writing files to directory \'' + outputdir +'\'! Check permissions.')
    print(Fore.RED + '\n[-] Failure to write output. Exiting program.')
    sys.exit(1)

#program success. we can exit naturally here
print(Fore.YELLOW + '\n[*] results written to directory ' + outputdir + '\n')