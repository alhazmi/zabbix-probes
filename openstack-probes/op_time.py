# This Python script is used to retrieve operation time since the creation of each tenant
# It uses the OpenStack endpoint APIs given in the configuration file
# "config.cfg" located at /usr/local/lib/

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin

import urllib
import urllib2
import re
import json
import list_tenants
import sys
from datetime import datetime, timedelta 

str_list = ''

def read_config(filename):
    f = open(filename, "r")

    dictionsry = {}
    for line in f:
        splitchar = '='
        kv = line.split(splitchar)
        if (len(kv)==2):
            dictionsry[kv[0]] = str(kv[1])[1:-2]
    return dictionsry

def op_time() :
    	try :
        	# read the configuration file from to the dictionary settings
        	settings=read_config("/usr/local/lib/config.cfg")
    	except :
        	print "Cannot read config.cfg"
        
	global str_list
	ten_vm = list_tenants.list_tenants()
	liste = []

	for i in range (len(ten_vm)) :
		str_list = str_list + ten_vm[i]["name"] + ": "
		uptime = 0

		try :
			token1_url = settings['identity_uri'] + "/tokens"
			token1_headers = {"Content-Type": "application/json", "Accept": "application/json"}
			token1_data = '{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "' + settings['username'] + '", "password": "' + settings['password'] + '"}}}'

			token1_req = urllib2.Request(token1_url, token1_data, token1_headers)
			token1_response = urllib2.urlopen(token1_req)
			get_token1 = token1_response.read()

			token1 = json.loads(get_token1)["access"]["token"]["id"]

			server_url = settings["compute_uri"] + "2dfbc4dfc2d042c8baf35e0fda7fc055/os-simple-tenant-usage/" + ten_vm[i]["id"] + "?start=" + settings["start"] + "&end=" + settings["end"]
			server_header = {"User-Agent": "python-novaclient", "X-Auth-Token": token1}

			server_req = urllib2.Request(server_url, None, server_header)
			server_response = urllib2.urlopen(server_req)
			get_servers = server_response.read()

			servers = json.loads(get_servers)["tenant_usage"]
		except urllib2.HTTPError, error:
    			sys.exc_clear()
    			servers = []

		if(len(servers) != 0) :
			now = datetime.now()
			if(ten_vm[i]["name"] == "admin") : #admin startdate is fixed
				start = datetime.strptime('2014-09-11T00:00:00.000000', '%Y-%m-%dT%H:%M:%S.%f')
				uptime = (now - start).days
			
			else :
				start = datetime.strptime(servers["start"], '%Y-%m-%dT%H:%M:%S.%f')
				uptime = (now - start).days

		if (i == len(ten_vm) - 1) :
			str_list = str_list + str(uptime) + " days"
		else : 
			str_list = str_list + str(uptime) + " days" + ', '

		dicti = {}
		dicti["name"] = ten_vm[i]["name"]
		dicti["uptime"] = uptime
		
		liste.append(dicti)
	return liste

op_time()

if __name__ == "__main__" :
    print str_list






