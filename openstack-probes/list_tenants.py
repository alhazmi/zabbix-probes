# This Python script is used to retrieve list of tenants in OpenStack
# It uses the OpenStack endpoint APIs given in the configuration file 
# "config.cfg" located at /usr/local/lib/

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin

from keystoneclient.v2_0 import client

str_list = '['

def read_config(filename):
    f = open(filename, "r")

    dictionsry = {}
    for line in f:
        splitchar = '='
        kv = line.split(splitchar)
        if (len(kv)==2):
            dictionsry[kv[0]] = str(kv[1])[1:-2]
    return dictionsry

def list_tenants() :
    try :
        # read the configuration file from to the dictionary settings
        settings=read_config("/usr/local/lib/config.cfg")
    except :
        print "Cannot read config.cfg"

    try :
        kc = client.Client(auth_url=settings["identity_uri"],username=settings["username"],password=settings["password"],tenant_name="admin")
        tlist_raw = kc.tenants.list()
    except :
        print "Cannot connect to Openstack Keystone Client"
        
    tlist = []
    global str_list

    for i in range(len(tlist_raw)) :
    	tdict = {}
    	tdict["name"] = tlist_raw[i].name
    	tdict["id"] = tlist_raw[i].id
        tlist.append(tdict)

        if i == len(tlist_raw) - 1 :
                str_list = str_list + tlist_raw[i].name + ']'
                break
        str_list = str_list + tlist_raw[i].name + ', '

    return tlist

list_tenants()

if __name__ == "__main__" :
	print str_list


