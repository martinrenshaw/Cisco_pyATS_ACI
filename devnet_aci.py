#!/usr/bin/python
import os
import sys
import json
import requests
from datetime import datetime
from prettytable import PrettyTable, ALL, FRAME, from_json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__author__ = "Martin Renshaw"
__copyright__ = "Copyright 2021, The DevNet MVP"
__credits__ = ["Martin Renshaw"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Martin Renshaw"
__email__ = "first.last@gmail.com"
__status__ = "Dev"


APIC_URL = "https://sandboxapicdc.cisco.com/"


def write_output(data, funcname):
    """ Write a file to the present working directory """
    today = datetime.now()
    if not os.path.exists('pyats-output'):
        os.mkdir('pyats-output')
    os.makedirs("pyats-output/"+today.strftime("%d-%m-%Y"), exist_ok=True)
    day = "pyats-output/"+today.strftime("%d-%m-%Y")
    with open(os.path.join(day, (today.strftime('%d-%m-%Y_%H%M%S')+funcname+'_output.json')), 'w') as outfile: 
        json.dump(data, outfile)

def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    tday = datetime.now()
    day = "pyats-output/"+tday.strftime("%d-%m-%Y")
    original = sys.stdout
    # Open the file in append & read mode ('a+')
    with open(os.path.join(day, (tday.strftime('%d-%m-%Y_%H%M')+file_name)), "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)
    sys.stdout = original


def apic_login():
    """ Login to APIC """

    token = ""
    err = ""

    try:
        response = requests.post(
            url=APIC_URL+"/api/aaaLogin.json",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps(
                {
                    "aaaUser": {
                        "attributes": {
                            "name": "admin",
                            "pwd": "!v3G@!4@Y"
                        }
                    }
                }
            ),
            verify=False
        )

        json_response = json.loads(response.content)
        token = json_response['imdata'][0]['aaaLogin']['attributes']['token']
        print('Authentication token:', token)

        print('Authentication Response Status: {status_code} \n'.format(
            status_code=response.status_code))
    except requests.exceptions.RequestException as err:
        print("HTTP Request failed")
        print(err)

    return token


def get_tenants():
    """ Get Tenants """

    token = apic_login()
    url=APIC_URL+"/api/node/class/fvTenant.json"
    print('GET request resource: ',url)

    try:
        response = requests.get(
            url,
            headers={
                "Cookie": "APIC-cookie=" + token,
                "Content-Type": "application/json; charset=utf-8",
            },
            verify=False
        )
        
        print('Response HTTP Status Code: {status_code}'.format(
           status_code=response.status_code))
        # print('Response HTTP Response Body:', json.dumps(response.json(), indent=4))  # uncomment to get full json print out
        json_response = json.loads(response.content)
        # data = json_response
        write_output(json_response, str('_tenant'))
        print("\nTotal Count of Tenants: "+json_response['totalCount']+"\n")
        for tenant in json_response['imdata']:
            print(tenant['fvTenant']['attributes']['dn'])

    except requests.exceptions.RequestException:
        print("HTTP Request failed")

def get_devices():
    """ Get Devices """
    pt = PrettyTable()
    pt.field_names = ["Role", "Name", "FabricState","Adst"]
    token = apic_login()
    url=APIC_URL+"/api/node/class/fabricNode.json?order-by=fabricNode.role|asc"
    print('GET request resource: ',url)

    try:
        response = requests.get(
                  url,
                  headers={
                    "Cookie": "APIC-cookie=" + token,
                    "Content-Type": "application/json; charset=utf-8"
                          },
                  verify=False)

        print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
        # print('Response HTTP Response Body:', json.dumps(response.json(), indent=4)) # uncomment to get full json print out
        json_response = json.loads(response.content)
        print("\nTotal Count Fabric Devices : "+json_response['totalCount']+"\n")
        for fabricdevices in json_response['imdata']:
            # print(mac['fvCEp']['attributes']['dn'])
            role = fabricdevices['fabricNode']['attributes']['role']
            name = fabricdevices['fabricNode']['attributes']['name']
            fabricSt = fabricdevices['fabricNode']['attributes']['fabricSt']
            AdSt = fabricdevices['fabricNode']['attributes']['adSt']
            # print(role+" "+name+" "+"FabricState = "+fabricSt+" AdSt = "+AdSt+"\n")
            pt.add_row([role,name,fabricSt,AdSt])
        print(pt)
        append_new_line('00_redirect.txt', '\n\nPrint all of the Fabrix Devices')
        append_new_line('00_redirect.txt', str(pt))

    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def get_mac_endpoint():
    """ Get the mac tables from the APIC and display neatly"""
    pt = PrettyTable()
    pt.field_names = ["Mac", "vLAN", "dn = Tenant / AP / EPG / EP","Interface"]
    token = apic_login()
    url=APIC_URL+"/api/node/class/fvCEp.json?rsp-subtree=children&order-by=fvCEp.encap"
    print('GET request resource: ',url)

    try:
        response = requests.get(
                  url,
                  headers={
                    "Cookie": "APIC-cookie=" + token,
                    "Content-Type": "application/json; charset=utf-8"
                          },
                  verify=False)

        print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
        # print('Response HTTP Response Body:', json.dumps(response.json(), indent=4)) # uncomment to get full json print out
        json_response = json.loads(response.content)
        write_output(json_response, str('_fvCEp_MAC'))
        print("\nTotal Count of MAC addrs : "+json_response['totalCount']+"\n")
        print("~"*10+" List of all MACs "+"~"*10+"\n")
        for mac in json_response['imdata']:
            # print(mac['fvCEp']['attributes']['dn'])
            print(mac['fvCEp']['attributes']['mac'])
        
        print("\n"*2+"~"*10+" List of all MACs with vLAN , DN & Path "+"~"*10+"\n")

        for maclist in json_response['imdata']:
            # print(mac['fvCEp']['attributes']['dn'])
            mac = maclist['fvCEp']['attributes']['mac']
            vlan = maclist['fvCEp']['attributes']['encap']
            dn = maclist['fvCEp']['attributes']['dn']
            pathep = maclist['fvCEp']['children'][0]['fvRsCEpToPathEp']['attributes']['tDn']
            # print(mac+"  "+vlan+"  "+dn+"  "+pathep)
            pt.add_row([mac,vlan,dn,pathep])
        print(pt)
        append_new_line('00_redirect.txt', '\n\nPrint all of the fvCEp MAC addrs ')
        append_new_line('00_redirect.txt', str(pt))
    except requests.exceptions.RequestException:
        print("HTTP Request failed")

def get_ip_endpoint():
    """ Get the mac tables from the APIC and display neatly"""
    pt = PrettyTable()
    pt.field_names = ["Mac", "vLAN", "dn = Tenant / AP / EPG / EP","IP addr"]
    token = apic_login()
    url=APIC_URL+"/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvIp&order-by=fvCEp.encap"
    print('GET request resource: ',url)

    try:
        response = requests.get(
                  url,
                  headers={
                    "Cookie": "APIC-cookie=" + token,
                    "Content-Type": "application/json; charset=utf-8"
                          },
                  verify=False)

        print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
        # print('Response HTTP Response Body:', json.dumps(response.json(), indent=4)) # uncomment to get full json print out
        json_response = json.loads(response.content)
        write_output(json_response, str('_fvCEp_IP'))
        # print("\nTotal Count of MAC addrs : "+json_response['totalCount']+"\n")
        print("~"*10+" List of all IP endpoints "+"~"*10+"\n")
        ipcount = []
        for endpoint in json_response['imdata']:
            for epIP in endpoint['fvCEp']['children']:
                print(epIP['fvIp']['attributes']['addr'])
                ipcount.append(epIP['fvIp']['attributes']['addr'])
        print('\n Total Count of all IP address end Points: ', len(ipcount))

        
        print("\n"*2+"~"*10+" List of all MACs with vLAN , DN & Path "+"~"*10+"\n")

        for iplist in json_response['imdata']:
            mac = iplist['fvCEp']['attributes']['mac']
            vlan = iplist['fvCEp']['attributes']['encap']
            dn = iplist['fvCEp']['attributes']['dn']
            # pt.add_row([mac,vlan,dn,'see above'])
            for epIP in iplist['fvCEp']['children']:
                pathep = epIP['fvIp']['attributes']['addr']
                pt.add_row([mac,vlan,dn,pathep])
                # pt.add_row(["-","-","-","-","-","-","-"])
                # pt.add_column("IP",[pathep])

            
        print(pt.get_string(sortby="dn = Tenant / AP / EPG / EP"))
        append_new_line('00_redirect.txt', '\n\nPrint all of the fvCEp IP addrs ')
        append_new_line('00_redirect.txt', str(pt))
    except requests.exceptions.RequestException:
        print("HTTP Request failed")

def get_rib():

    pt = PrettyTable()
    pt.field_names = ["PREFIX", "DN"]
    """ Get the IPv4 RIB from the APIC """
    token = apic_login()
    url=APIC_URL+"/api/class/uribv4Route.json?order-by=uribv4Route.prefix|asc"  # Gets the full RIB from all fabric Nodes
    print('GET request resource: ',url)

    try:
        response = requests.get(
                  url,
                  headers={
                    "Cookie": "APIC-cookie=" + token,
                    "Content-Type": "application/json; charset=utf-8"
                          },
                  verify=False)

        print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
        # print('Response HTTP Response Body:', json.dumps(response.json(), indent=4)) # uncomment to get full json print out
        json_response = json.loads(response.content)
        write_output(json_response, str('_uribv4Route'))
        print("\nTotal Count of RIB entries : "+json_response['totalCount']+"\n")
        for pf in json_response['imdata']:
            print(pf['uribv4Route']['attributes']['prefix']+"  "+pf['uribv4Route']['attributes']['dn'])
            prefix = pf['uribv4Route']['attributes']['prefix']
            dn = pf['uribv4Route']['attributes']['dn']
            pt.add_row([prefix,dn])
        print(pt)
        append_new_line('00_redirect.txt', '\n\nPrint all of the uribv4Route Prfixes ')
        append_new_line('00_redirect.txt', str(pt))
    except requests.exceptions.RequestException:
        print("HTTP Request failed")




# Suppress credential warning for this exercise
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print("\n"+40*'='+' GET TENANTS '+'='*40+"\n")
get_tenants()
print("\n"+40*'='+' GET FABRIC '+'='*40+"\n")
get_devices()
print("\n"+40*'='+' GET FABRIC GLOBAL END POINTS - MAC END POINTS '+'='*40+"\n")
get_mac_endpoint()
print("\n"+40*'='+' GET FABRIC GLOBAL END POINTS - IP  END POINTS '+'='*40+"\n")
get_ip_endpoint()
print("\n"+40*'='+' GET RIB TABLE '+'='*40+"\n")
get_rib()


print("\n"+40*'='+" OUTPUT FILES ARE LOCATED AT /pwd/pyats-output/....."+'='*40+"\n")
