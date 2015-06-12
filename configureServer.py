
# Copy right (c) 2013, Yahya Al-hazmi , Technische Universitaet Berlin

# Reads the metrics from a file recevied as input and registeres them to the Zabbix server using Zabbix API
# It is called internally by zabbix-add-metric
 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
#

import sys
import time
sys.path.append("/usr/local/lib/")
from zabbix_api import ZabbixAPI

def read_config(filename):
    try:
        f = open(filename, "r")
    except:
        logger.error("can not read file %s, script terminated" % (filename))
        sys.exit()
    try:
        dictionsry = {}
        for line in f:
            splitchar = '='
            kv = line.split(splitchar)
            if (len(kv)==2):
                dictionsry[kv[0]] = str(kv[1])[1:-2]
        return dictionsry
    except:
        logger.error("can not read file %s to a dictionary, format must be KEY=VALUE" % (filename))
        sys.exit()

class Agent:
	def __init__(self):
		print "Initialization"
	def parseMetricskeysFile(self, filename):
		metrics = []
		try:
			f = open(filename, 'r')
			for line in f: 
				if line[0]=="#":
					continue
				#without the \n
				metrics.append(line[:-1])
			f.close()
		except IOError:
			print "metricskeys file does not exist"
		return metrics

        def parseMetricsratesFile(self, filename):
                metrics = []
                try:
                        f = open(filename, 'r')
                        for line in f:
                                if line[0]=="#":
                                        continue
                                #without the \n
                                metrics.append(line[:-1])
                        f.close()
                except IOError:
                        print "metricsrates file does not exist"
                return metrics

        def parseMetricsvaluetypesFile(self, filename):
                metrics = []
                try:
                        f = open(filename, 'r')
                        for line in f:
                                if line[0]=="#":
                                        continue
                                #without the \n
                                metrics.append(line[:-1])
                        f.close()
                except IOError:
                        print "metricsvaluetypes file does not exist"
                return metrics

        def parseMetricshistoriesFile(self, filename):
                metrics = []
                try:
                        f = open(filename, 'r')
                        for line in f:
                                if line[0]=="#":
                                        continue
                                #without the \n
                                metrics.append(line[:-1])
                        f.close()
                except IOError:
                        print "metricshistories file does not exist"
                return metrics
	
	def addMetricsToServer(self, username, password, serverip, hostname, metricskeysfile, metricsratesfile, metricsvaluetypesfile, metricshistoriesfile):
		metricskeys = self.parseMetricskeysFile(metricskeysfile)
		print metricskeys
                metricsrates = self.parseMetricsratesFile(metricsratesfile)
                print metricsrates
                metricsvaluetypes = self.parseMetricsvaluetypesFile(metricsvaluetypesfile)
                print metricsvaluetypes 
                metricshistories = self.parseMetricshistoriesFile(metricshistoriesfile)
                print metricshistories
		server ="http://"+serverip+""
		zapi = ZabbixAPI(server=server, path="", log_level=6)
		zapi.login(username, password)

		hostid = zapi.host.get({"filter":{"host":hostname}, "output":"short"})[0]["hostid"]				
		print hostid
		interfaceid = zapi.hostinterface.get({"filter":{"host":hostname}, "output":"short"})[0]["interfaceid"]

		#get application
		applicationName = "User Items"
		applications = zapi.application.get({"filter":{"name":applicationName, "hostid":hostid}})
		if len(applications) == 0:
			appid = zapi.application.create([{"name":applicationName, "hostid":hostid}])["applicationids"][0]
		else:
			appid = applications[0]["applicationid"]		
		print appid

		#adding only new items but not the already existing ones
                oldbitems = zapi.item.get({"filter":{"hostid":hostid}, "applicationids":[appid], "output":"extend"})
                oldkeys = []
                for olditem in oldbitems:
                        olditemkey = olditem["key_"]
                        if olditemkey in metricskeys:
                                oldkeys.append(olditemkey)
 		for i in range(len(metricskeys)):
			if metricskeys[i] not in oldkeys:
                                description = "User generated: "+metricskeys[i]
                                if metricsrates[i] == "NO_PRO":
                                        rate =30  #use default value
                                else:
                                        rate = metricsrates[i]
                                if metricsvaluetypes[i] == "NO_PRO":
                                        valuetype = 1  #use default value
                                else:
                                        valuetype = metricsvaluetypes[i]
                                if metricshistories[i] == "NO_PRO":
                                        history = 7  #use default value
                                else:
                                        history = metricshistories[i]
				zapi.item.create({'name': (metricskeys[i]),'hostid' : (hostid),"interfaceid" : interfaceid, 'description' : (description),'key_' : metricskeys[i],'type' : 0, "applications":[appid], "delay": rate, "value_type": valuetype, "history": history})


try:
	settings=read_config('/usr/local/lib/config.cfg')
except:
	logger.error("can not read file config.cfg in /usr/local/lib/.")
	sys.exit()
		
agent = Agent()

serverip = sys.argv[1]
hostname = sys.argv[2]
metricskeysfile = sys.argv[3]
metricsratesfile = sys.argv[4]
metricsvaluetypesfile = sys.argv[5]
metricshistoriesfile = sys.argv[6]

maxcount = 10
if serverip == "127.0.0.1":
    maxcount = 3
count = 0

while count < maxcount:
    try:
	agent.addMetricsToServer(settings['zabbixusername'], settings['zabbixpassword'], serverip, hostname, metricskeysfile, metricsratesfile, metricsvaluetypesfile, metricshistoriesfile)
    except:
        print "Something goes wrong, wait 60s and retry"
        time.sleep(60)
        count = count + 1
    else:
        print "Metric correctly added, exit"
        break
