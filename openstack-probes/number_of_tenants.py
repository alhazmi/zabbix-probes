# This Python script is used to retrieve number of deployed tenants 
# It uses the OpenStack endpoint APIs given in the configuration file
# "config.cfg" located at /usr/local/lib/

# Copy right (c) 2014, Yahya Al-Hazmi, Technische Universitaet Berlin


import list_tenants

num = 0

def get_number() :
	global num
	tenants = list_tenants.list_tenants()
	num = int(len(tenants))

	return num

get_number()

if __name__ == "__main__" :
    print num

    
