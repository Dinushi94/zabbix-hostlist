#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

# getBulkStatus.py -Z http://yourserver/zabbix -u admin -p somePass

# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'

# ./getBulkStatus.py
HostID: 10084 - HostName: Zabbix server - IP: 127.0.0.1 - Type: agent - Status: 0
HostID: 10339 - HostName: Product1-Ubuntu - IP: 15.222.237.42 - Type: agent - Status: 0
HostID: 10340 - HostName: Product2-Ubuntu - IP: 35.183.78.59 - Type: agent - Status: 1

CSV output
10084,Zabbix server,127.0.0.1,agent,ENABLE
10339,Product1-Ubuntu,15.222.237.42,agent,ENABLE
10340,Product2-Ubuntu,35.183.78.59,agent,DISABLE


"""

from zabbix.api import ZabbixAPI
import sys
import argparse
import time
import datetime
import os
import json
import csv

# Class for argparse env variable support


class EnvDefault(argparse.Action):
    # From https://stackoverflow.com/questions/10551117/
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def jsonPrint(jsonUgly):
    print(json.dumps(jsonUgly, indent=4, separators=(',', ': ')))


def ArgumentParser():
    parser = argparse.ArgumentParser()

#     parser.add_argument('-Z',
#                         required=True,
#                         action=EnvDefault,
#                         envvar='ZABBIX_SERVER',
#                         help="Specify the zabbix server URL ie: http://yourserver/zabbix/ (ZABBIX_SERVER environment variable)",
#                         metavar='zabbix-server-url')

#     parser.add_argument('-u',
#                         required=True,
#                         action=EnvDefault,
#                         envvar='ZABBIX_USERNAME',
#                         help="Specify the zabbix username (ZABBIX_USERNAME environment variable)",
#                         metavar='Username')

#     parser.add_argument('-p',
#                         required=True,
#                         action=EnvDefault,
#                         envvar='ZABBIX_PASSWORD',
#                         help="Specify the zabbix username (ZABBIX_PASSWORD environment variable)",
#                         metavar='Password')

    parser.add_argument('-f',
                        required=False,
                        help="Hostname to search",
                        metavar='hostname')

    return parser.parse_args()


def main(args):
    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = "http://example.com/"
    zabbixUsername = "username"
    zabbixPassword = "password"
    hostNameFilter = args.f

    interfaceType = {
        '1': 'agent',
        '2': 'SNMP',
        '3': 'IPMI',
        '4': 'JMX',
    }

    bulkStatus = {
        '0': 'OFF',
        '1': 'ON',
    }

    hostStatus = {
        '0': 'ENABLE',
        '1': 'DISABLE',
    }

    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,password=zabbixPassword)

    if (hostNameFilter):
        # Filter based on the cmdline argument
        f = {'host': hostNameFilter}
        hosts = zapi.host.get(search=f, output='extend', selectTags='extend')
        interfaces = zapi.hostinterface.get(hostids=hosts[0]['hostid'])
    else:
        interfaces = zapi.hostinterface.get()
        hosts = zapi.host.get(output='extend')

    #Terminal Print Start
    for interface,host in zip(interfaces,hosts):
        if (interface['type']=='1' and host['host']):
            print('HostID: {} - HostName: {} - IP: {} - Type: {} - Status: {}'.format(
                    interface['hostid'], host['host'], interface['ip'], interfaceType[interface['type']], host['status']))
    #Terminal Print End

    #Start CSV
    with open('icd.csv','w') as csvfile:
        fieldnames=['HostID','HostName','IP','Status']
        thewriter=csv.DictWriter(csvfile,fieldnames=fieldnames)

        thewriter.writeheader()
        for interface,host in zip(interfaces,hosts):
            if (host['host'] and host['status']=='0'):
                thewriter.writerow({'HostID':interface['hostid'],'HostName':host['host'],'IP':interface['ip'],
                    'Status':hostStatus[host['status']]})
    #End CSV      
        

if __name__ == "__main__":
    main(sys.argv[1:])
