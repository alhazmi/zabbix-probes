#!/usr/bin/env python

# This Python script is used to create tenant related metrics in Zabbix 
# each tenant is represnted through a hostgroup in Zabbix 
# This script uses configuration file "config.cfg" located at /usr/local/lib/
# It also uses zabbix_api.py located at /usr/local/lib for configuring zabbix

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin

sys.path.append("/usr/local/lib/")
from zabbix_api import ZabbixAPI
import list_instances
import sys
import random

str_res = 0

def read_config(filename):
    f = open(filename, "r")

    dictionsry = {}
    for line in f:
        splitchar = '='
        kv = line.split(splitchar)
        if (len(kv)==2):
            dictionsry[kv[0]] = str(kv[1])[1:-2]
    return dictionsry

# read the configuration file from to the dictionary settings
settings=read_config("/usr/local/lib/config.cfg")
append = True
for i in sys.path :
	if (i == settings["libpath"]) :
		append = False
if (append == True) :
	sys.path.append(settings["libpath"])

from zabbix_api import ZabbixAPI

def create_hgroup() :
	global str_res

	try:
		zapi = ZabbixAPI(settings["zabbixurl"])
		zapi.login(settings["zabbixusername"],settings["zabbixpassword"])

		var = list_instances.list_instances() # list of dictionaries (name, id, vm)

	except Exception, error:
		print "Error connecting to Zabbix"
		raise error

	try:
		mon_se = zapi.host.get({"filter": {"host": "monitoringservicese"}})[0]["hostid"]
		for i in range(len(var)) :
			if var[i]["vm"] :	# if instances not empty (1)
				tenant_exist = False
				instances_exist = False
				hgroup_get = zapi.hostgroup.get({"output": "extend"})
				if hgroup_get :	# if hostgroup list not empty
					for hgroup in hgroup_get :
						if (var[i]["name"] in hgroup["name"]) and ("tenant" in hgroup["name"]) :	# check if tenant already in host group list
							tenant_exist = True

				result2 = zapi.host.get({"output": "extend"})
				if result2 :
					for n in var[i]["vm"] :	# check if instances are monitored, if not abort
						for m in result2 :
							if(n.lower() in m["name"].lower()) :
								instances_exist = True
								break

				if (not tenant_exist) and (instances_exist):	# if hostgroup list empty or tenant hasn't been added to hostgroup or instances are monitored
					result = zapi.hostgroup.create([{"name": var[i]["name"] + "_tenant"}])

					for k in range (len(var[i]["vm"])):
						for j in range(len(result2)) :
							if var[i]["vm"][k].lower() in result2[j]["name"].lower() :
								zapi.hostgroup.massAdd({"groups": [{"groupid": result["groupids"][0]}], "hosts": [{"hostid": result2[j]["hostid"]}]})

				elif tenant_exist and instances_exist :	# check existing hostgroups if the hosts really match the ones from openstack
					ten_id = zapi.hostgroup.get({"output": "extend", "filter": {"name": var[i]["name"] + "_tenant"}})[0]["groupid"]
					hosts = zapi.host.get({"output": "extend", "groupids": ten_id})
					add = False

					for k in range (len(var[i]["vm"])):
						for m in range (len(result2)) :
							if var[i]["vm"][k].lower() in result2[m]["name"].lower() :
								for j in range(len(hosts)) :
									if var[i]["vm"][k].lower() not in hosts[j]["host"].lower() :
										add = add and True
									else :
										add = add and False
							if add :
								zapi.hostgroup.massAdd({"groups": [{"groupid": ten_id}], "hosts": [{"hostid": result2[m]["hostid"]}]})
								add = False

				#aggregated items and graphs
				app = zapi.application.get({"filter": {"name": "tenant"}})[0]["applicationid"]
				
				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :		
					if not zapi.item.get({"filter": {"name": "Used bandwidth_" + var[i]["name"]}}) :
						res1 = zapi.item.create({"name": "Used bandwidth_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"net.if.out[eth0]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 3, "data_type": 0, "units": "bps", "multiplier": 1, "formula": 8, "delay": 60, "history": 7, "applications": [app]})
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Used bandwidth_' + var[i]["name"]}) :
							zapi.graph.create({"name": "Used bandwidth_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 0, "gitems": [{"itemid": res1["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res1["itemids"][0], "color": color}]})

						str_res = str_res or 1

				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :	
					if not zapi.item.get({"filter": {"name": "Used CPU user time_" + var[i]["name"]}}) :
						res2 = zapi.item.create({"name": "Used CPU user time_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"system.cpu.util[,user]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 0, "units": "%", "multiplier": 0, "delay": 60, "history": 7, "applications": [app]})
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Used CPU user time_' + var[i]["name"]}) :
							zapi.graph.create({"name": "Used CPU user time_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 0, "gitems": [{"itemid": res2["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res2["itemids"][0], "color": color}]})
						
						str_res = str_res or 1
					
				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :	
					if not zapi.item.get({"filter": {"name": "Used memory_" + var[i]["name"]}}) :
						res3 = zapi.item.create({"name": "Used memory_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"vm.memory.size[used]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 3, "data_type": 0, "units": "B", "multiplier": 0, "delay": 30, "history": 90, "applications": [app]})
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Used memory_' + var[i]["name"]}) :
							zapi.graph.create({"name": "Used memory_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 0, "gitems": [{"itemid": res3["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res3["itemids"][0], "color": color}]})

						str_res = str_res or 1

				# aggregated allocated items
				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :	
					if not zapi.item.get({"filter": {"name": "Allocated Harddisk_" + var[i]["name"]}}) :
						res4 = zapi.item.create({"name": "Allocated Harddisk_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"vfs.fs.size[/,total]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 3, "units": "B", "data_type": 0, "multiplier": 0, "delay": 30, "history": 7, "applications": [app]})
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Allocated Harddisk_' + var[i]["name"]}) :
							zapi.graph.create({"name": "Allocated Harddisk_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 2, "gitems": [{"itemid": res4["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res4["itemids"][0], "color": color}]})

						str_res = str_res or 1

				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :
					if not zapi.item.get({"filter": {"name": "Allocated RAM_" + var[i]["name"]}}) :
						res5 = zapi.item.create({"name": "Allocated RAM_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"vm.memory.size[total]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 3, "units": "B", "data_type": 0, "multiplier": 0, "delay": 30, "history": 7, "applications": [app]})	
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Allocated RAM' + var[i]["name"]}) :
							zapi.graph.create({"name": "Allocated RAM_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 2, "gitems": [{"itemid": res5["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res5["itemids"][0], "color": color}]})

						str_res = str_res or 1

				if zapi.hostgroup.exists({"name": var[i]["name"] + "_tenant"}) :	
					if not zapi.item.get({"filter": {"name": "Allocated VCPU_" + var[i]["name"]}}) :
						res6 = zapi.item.create({"name": "Allocated VCPU_" + var[i]["name"], "key_": "grpsum[\"" + var[i]["name"] + "_tenant\",\"system.cpu.num[]\",last,0]", "hostid": mon_se, "type": 8, "value_type": 3, "data_type": 0, "multiplier": 0, "delay": 30, "history": 7, "applications": [app]})
						
						color = "%06x" % random.randint(0,0xFFFFFF)
						if not zapi.graph.exists({"name": 'Allocated VCPU_' + var[i]["name"]}) :
							zapi.graph.create({"name": "Allocated VCPU_" + var[i]["name"], "width": 900, "height": 200, "graphtype": 2, "gitems": [{"itemid": res6["itemids"][0], "color": color}]})
						#else : #if already exists
						#	zapi.graph.update({"gitems": [{"itemid": res6["itemids"][0], "color": color}]})

						str_res = str_res or 1	


		return str_res

	except Exception, error: 
	 	print "Error creating Hostgroup"
	 	print error

create_hgroup()

if __name__ == "__main__" :
	print str_res


#(1) if tenant doesn't have instances, no hostgroup will be created





