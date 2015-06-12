#!/usr/bin/python

# This Python script is used to add log metrics to Zabbix in order to monitor logging
# files run on the host, in which this script is executed.
# Zabbix agent should be running on this host, otherwise this script will not do anything
# Zabbix API Python Library (zabbix_api.py) is required to run this script.

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin

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

import sys, getopt
sys.path.append("/usr/local/lib/")
from zabbix_api import ZabbixAPI
import ast

def read_config(filename):
    f = open(filename, "r")

    dictionsry = {}
    for line in f:
        splitchar = '='
        kv = line.split(splitchar)
        if (len(kv)==2):
            dictionsry[kv[0]] = str(kv[1])[1:-2] # without ""
    return dictionsry

try:
	settings=read_config('/usr/local/lib/config.cfg')
except:
	logger.error("can not read file config.cfg in /usr/local/lib/.")
	sys.exit()

server = settings['zabbixurl']

def getHostList() :
   zapi = ZabbixAPI(server=server)
   zapi.login(settings['zabbixusername'], settings['zabbixpassword'])

   result = zapi.host.get({"output": "extend"})
   hostlist = []
   for i in result :
      hostlist.append(i["name"])
   return hostlist

def printHostList() :
   zapi = ZabbixAPI(server=server)
   zapi.login(settings['zabbixusername'], settings['zabbixpassword'])

   result = zapi.host.get({"output": "extend"})
   hostlist = []
   for i in result :
      print i["name"]

def type_of_value(var):
 try:
    return type(ast.literal_eval(var))
 except Exception:
    return str

def main(argv):
   key = ''
   path = ''
   rate = ''
   history = ''
   hostname =''

   try:
      opts, args = getopt.getopt(argv,"uln:k:p:r:h:",["hostname=","key=","path=","rate=","history="])
   except getopt.GetoptError:
      print 'type -u to see the correct arguments input'
      sys.exit(2)

   if(len(sys.argv) <= 1) :
      print 'type -u to see the correct arguments input'
      sys.exit()

   for opt, arg in opts:
      if opt == '-u':
         print 'This script allows you to add logging data from a file of one of the already monitored hosts.'
         print 'To see the list of currently monitored hostnames:'
         print 'add-log-metrics.py -l'
         print ''
         print 'Enter your metrics one by one using the following pattern, otherwise, the added metrics will not work:'
         print 'add-log-metrics.py -n <hostname> -k <key> -p <path> -r <rate> -h <history>'
         print ''
         print '<hostname>: name of the monitored host on which the log file is located. Please enter the name as appeared in the list'
         print '<key> = represents the name of the metric'
         print '<path> = a complete path to the log file'
         print '<rate> = the update interval in seconds [Default value: 30] (optional)'
         print '<history> = history of the monitoring information in days [Default value: 7] (optional)'
         print 'EXAMPLE: add-log-metrics.py -n monitoringservicese -k testLog -p /var/log/test.log -r 20, -h 80'

         sys.exit()
      elif opt == '-l':
         print 'The currently monitored hosts are:'
         printHostList()
         sys.exit()
      elif opt in ("-n", "--hostname"):
         hostname = arg
      elif opt in ("-k", "--key"):
         key = arg
      elif opt in ("-p", "--path"):
         path = arg
      elif opt in ("-r", "--rate"):
         rate = arg
      elif opt in ("-h", "--history"):
         history = arg

   if (hostname == '' or key == '' or path == '') :
      print 'You need to enter all the appropriate arguments'
      sys.exit()

   if (rate != '' and type_of_value(rate) != int) :
      print 'Please enter the correct input of rate'

   if (history != '' and type_of_value(history) != int) :
      print 'Please enter the correct input of history'   

   hostlist = getHostList()
   host_check = False
   for i in hostlist :
      if (i == hostname) :
         host_check = True

   if(host_check == False) :
      print 'You need to enter the hostname exactly as it appears on the list'
      sys.exit()

   print 'Hostname is', hostname
   print 'Key is', key
   print 'Path is', path
   if (rate == '') :
      print 'Rate is 30 second(s) [Default]' 
   else :
      print 'Rate is', rate, 'second(s)'
   if (history == '') :
      print 'History is 7 day(s) [Default]' 
   else :
      print 'History is', history, 'day(s)'
   print ''

   zapi = ZabbixAPI(server=server, path="", log_level=6)
   zapi.login(settings['zabbixusername'], settings['zabbixpassword'])

   hostid = zapi.host.get({"filter":{"host":hostname}, "output":"short"})[0]["hostid"]
   #print hostid

   #get application
   applicationName = "Logs"
   applications = zapi.application.get({"filter":{"name":applicationName, "hostid":hostid}})
   if len(applications) == 0:
         appid = zapi.application.create([{"name":applicationName, "hostid":hostid}])["applicationids"][0]
   else:
         appid = applications[0]["applicationid"]
   #print appid

   #adding only new items but not the already existing ones
   if zapi.item.get({"filter":{"hostid":hostid, "name": key}, "applicationids":[appid], "output":"extend"}) :
      print "Metric with that name already exists. Exiting now..."
      sys.exit()
   elif zapi.item.get({"filter":{"hostid":hostid, "key_": 'log[' + path + ']'}, "applicationids":[appid], "output":"extend"}) :
      print "Metric with that path already exists. Exiting now..."
      sys.exit()
   else :
      if (rate == '') :
         rate = 30 #default
      if (history == '') :
         history = 7 #default

      zapi.item.create({'name': key,'hostid' : hostid, 'key_' : 'log[' + path + ']','type' : 7, "applications":[appid], "delay": rate, "value_type": 2, "history": history, "logtimefmt": 'pppppp:yyyyMMdd:hhmmss'})

   print "Metric successfully created."

if __name__ == "__main__":
   main(sys.argv[1:])





