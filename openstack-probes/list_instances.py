# This Python script is used to retrieve list of instances per tenant  
# It uses the OpenStack endpoint APIs given in the configuration file 
# "config.cfg" located at /usr/local/lib/

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin


from novaclient.v1_1 import client
import list_tenants
import sys

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

def list_instances() :
    try :
        # read the configuration file from to the dictionary settings
        settings=read_config("/usr/local/lib/config.cfg")
    except :
        print "Cannot read config.cfg"

    global str_list
    res = []

    tenants = list_tenants.list_tenants()

    for i in range(len(tenants)) :
        ilist = []
        ilist_raw = []

        str_list = str_list + tenants[i]["name"] + ": ["

        try:
            nc = client.Client(username=settings['username'], 
                                api_key=settings['password'], 
                                project_id=tenants[i]["name"], 
                                auth_url=settings['identity_uri'], 
                                service_type='compute')

            ilist_raw = nc.servers.list()

        except Exception, e :   #EndpointNotFound, Unauthorized
            sys.exc_clear() 

        if(len(ilist_raw) == 0) :
            if(i != len(tenants) - 1) :
                str_list = str_list + "], "
            else :
                str_list = str_list + "]"
        else :
            for j in range (len(ilist_raw)) :
                ilist.append(ilist_raw[j].name) 

                if(j == len(ilist_raw) - 1) :
                    str_list = str_list + ilist_raw[j].name
                    if(i != len(tenants) - 1) :
                        str_list = str_list + "], "
                    else :
                        str_list = str_list + "]"
                else :
                    str_list = str_list + ilist_raw[j].name + ", "

        ten_ilist = {}
        ten_ilist["name"] = tenants[i]["name"]
        ten_ilist["id"] = tenants[i]["id"]
        ten_ilist["vm"] = ilist
        res.append(ten_ilist)

    return res

list_instances()

if __name__ == "__main__" :
    print str_list




