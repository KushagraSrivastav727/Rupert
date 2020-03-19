import re
import sys
import requests
import subprocess
from termcolor import colored
from multiprocessing import Pool
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


#default values
verbose = False
bruteforce = False
from_file = False
domains = []

#parse domain input
if len(sys.argv) > 1:
	#list of domains to be checked
	if str(sys.argv[1]) == "-i":
		from_file = str(sys.argv[2])
	
	else:
		domains.append(str(sys.argv[1]))


#parse additional arguments
if len(sys.argv) > 2:
	for arg in sys.argv:
		#set verbosity level
		if arg == "-v":
			verbose = True

		#set bruteforce level
		if arg == "-b":
			bruteforce = True


#subdomain takeover detection data from EdOverflow
takeover_data = {
	"AWS/S3": "The specified bucket does not exist",
	"Bitbucket": "Repository not found",
	"Campaign Monitor": "'Trying to access your account?'",
	"Fastly": "Fastly error: unknown domain:",
	"Feedpress": "The feed has not been found.",
	"Ghost": "The thing you were looking for is no longer here, or never was",
	"Github": "There isn't a Github Pages site here.",
	"HatenaBlog": "404 Blog is not found",
	"Help Juice": "We could not find what you're looking for.",
	"Help Scout": "No settings were found for this company:",
	"Heroku": "No such app",
	"Intercom": "Uh oh. That page doesn't exist.",
	"JetBrains": "is not a registered InCloud YouTrack",
	"Kinsta": "No Site For Domain",
	"LaunchRock": "It looks like you may have taken a wrong turn somewhere. Don't worry...it happens to all of us.",
	"Mashery": "Unrecognized domain",
	"Pantheon": "404 error unknown site!",
	"Readme.io": "Project doesnt exist... yet!",
	"Shopify": "Sorry, this shop is currently unavailable.",
	"Surge.sh": "project not found",
	"Tumblr": "Whatever you were looking for doesn't currently exist at this address",
	"Tilda": "Please renew your subscription",
	"UserVoice": "This UserVoice subdomain is currently available!",
	"Wordpress": "Do you want to register "
}


def generic(domain):
	#gather subdomains
	subdomains = subfinder(domain)

	#use sublist3r with bruteforce module to find subdomains
	if bruteforce == True:
		subbruted = subbrute(domain)

		#add bruteforced domain to list if not already found
		for bruteforced_domain in subbruted:
			if bruteforced_domain not in subdomains:
				subdomains.append(bruteforced_domain)

	return subdomains

#organically gather subdomains
def subfinder(domain):
	subdomains = subprocess.check_output('./subfinder/subfinder -silent -d %s -o subfinder/output/%s' % (domain, domain), shell=True)

	return subdomains.decode('utf-8').split('\n')[:-1]


#bruteforce subdomains
def subbrute(domain):
	subdomains = subprocess.check_output('cd subbrute; python3 subbrute.py %s -o output/%s -s ../wordlists/bitquark-subdomains-top100000.txt -c 50' % (domain, domain), shell=True)

	return subdomains.decode('utf-8').split('\n')


#discern if domain is vulnerable to a subdomain takeover
def is_yoinkable(domain):
	try:
		#check if is http or https
		r = requests.get("http://" + domain, timeout=5, verify=False)

		if r.url.split("://")[0] == "https://":
			r = requests.get("https://" + domain)

		#check if takeover fingerprint exists in page
		for engine in takeover_data:
			if takeover_data[engine] in r.text:
				#make output all purdy
				whitespace = ""
				whitespace_length = 45 - len(domain)
				
				for i in range(whitespace_length):
					whitespace += " "

				print(colored(domain, 'cyan'), colored("%s%s",'white') % (whitespace, engine))

				with open("./zoinks/" + domain, "w+") as file:
					file.write(engine)

				return True

		if verbose:
			print(colored(domain, 'green'))

	except:
		return False


#read domains from file
if from_file:
	for line in open(from_file, "r").readlines():
		domains.append(line.rstrip('\n'))


#test the list of domains
for domain in domains:
	print(colored(domain, 'grey'))

	subdomains = generic(domain)


	print(colored('Total: %s domains found', 'white') % str(len(subdomains)))
	print('')

	p = Pool(processes=20)
	result = p.map(is_yoinkable, subdomains)
