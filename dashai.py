#!/usr/bin/python
""" DashAi is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License

    DashAi is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DashAi. 
"""

from __future__ import print_function
import random
import os
from subprocess import call
import httplib2
import json
import webbrowser
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import time
from datetime import datetime, date, time, timedelta
import dateutil.parser as parser
from dateutil.tz import tzlocal


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# Function definition is here
def deploycore():
      os.system('clear')
      os.system('sleep 5')
      print("Loging in as system")
      call(["oc", "login", "https://192.168.99.100:8443", "-u", "system:admin"])
      print("Creting DashAi Project")
      call(["oc", "new-project", "dashai"])
      print("Prep Project Steps [run as admin]")
      call(["oc", "adm", "policy", "add-scc-to-user", "anyuid", "-z", "default"])
      call(["oc", "adm", "policy", "add-cluster-role-to-user", "cluster-reader", "-z", "default"])
      print(" Deploying Grafana")
      call(["oc", "new-app", "grafana/grafana"])
      call(["oc", "volume", "dc/grafana", "--remove", "--name=grafana-volume-1"])
      call(["oc", "volume", "dc/grafana", "--remove", "--name=grafana-volume-2"])
      call(["oc", "expose", "service", "grafana"])
      print(" Deploying InfluxDB ")
      call(["oc", "new-app", "https://github.com/alyarctiq/myinfluxdb", "--name", "myinfluxdb"])
      print('\n')
      print('\n')
      call(["oc", "expose", "service", "myinfluxdb"])
      call(["oc", "status"])
      raw_input("Press Enter to continue...")
      os.system('clear')
      return;

def deploynagios():
      print("Deploying Nagios")
      print("Operations Monitoring Stack")
      command="oc new-app https://github.com/alyarctiq/mydb --name mydb"
      call(command, shell=True)
      command="oc new-app https://github.com/alyarctiq/gearmand --name gearmand"
      call(command, shell=True)
      command="oc new-app https://github.com/alyarctiq/modworker --name modworker"
      call(command, shell=True)
      command="oc new-app https://github.com/alyarctiq/nagflux --name nagflux"
      call(command, shell=True)
      command="oc new-app https://github.com/alyarctiq/nagios --name nagios"
      call(command, shell=True)
      print('\n')
      print('\n')
      command="oc status"
      call(command, shell=True)
      print('\n')
      print('INFO: This deployment will take a bit of time to build, please be patient :) ')
      raw_input("Press Enter to continue...")
      os.system('clear')
      return;

def deployocp():
      print("Deploying Prometheus")
      command="oc new-app prom/prometheus"
      call(command, shell=True)
      #call(["oc", "create", "-f", "https://github.com/alyarctiq/myprometheus/blob/master/prom-configmap.yml"])
      command="oc create -f https://raw.githubusercontent.com/debianmaster/openshift-examples/master/promethus/prom-configmap.yml"
      call(command, shell=True)
      print("Apply Config Map")
      command="oc volume dc/prometheus --add --name=prom-k8s -m /etc/prometheus -t configmap --configmap-name=prom-k8s"
      call(command, shell=True)
      command="oc expose service prometheus"
      call(command, shell=True)
      print('\n')
      print('\n')
      command="oc status"
      call(command, shell=True)
      raw_input("Press Enter to continue...")
      os.system('clear')
      return;

def deployjenkins():
      os.system('clear')
      print("Jenkins Integration")
      print("Exposing InfluxDB..")
      print("\nPlease follow instruction here to enable Jenkins + InfluxDB Integration")
      print("https://wiki.jenkins.io/display/JENKINS/InfluxDB+Plugin")
      print("and enter the below as the end-point")
      print("\n")
      call(["oc", "get", "routes", "myinfluxdb"])
      raw_input("Press Enter to continue...")
      os.system('clear')
      return;

def deployjira():
      os.system('clear')
      print ("""
        Instructions:
        1) Git Clone Our jira-DashAi repo <http://...>
        2) Edit config.json
        3) Add the InfluxDB URL, database, username, and password (leave the last two blank if you did not configure auth/authz).
            HINT: for InfluxDB URL -> check Main Menu -> MyInfluxDB-URL
        4) Commit back to your repo.
        5) Enter you Git Repo in the next step and we will build your jira-dashi pod!

        What would you like to do next?
        1) Provide GitRepo
        2) Back to main menu

          """)
      ans=raw_input("What would you like to do? ")
      if ans=="1":
          print('\n Enter Your GitRepo')
          print('\n Example https://github.com/ArctiqTeam/dashai/')
          gitrepo=raw_input("Enter GitRepo: ")
      elif ans=="2":
          return

      print("Creating InfluxDB for JIRA")
      os.system('./build-influxdb.sh')
      raw_input("Press Enter to continue...")
      #curl -G http://myinfluxdb-dashai.192.168.99.100.nip.io/query --data-urlencode "q=CREATE DATABASE mydb;" -X POST
      os.system('clear')
      return;

def get_client_token():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.dashai')
    credential_path = os.path.join(credential_dir,'client_secret.json')
    return credential_path

def get_private_token():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.dashai')
    credential_path = os.path.join(credential_dir,'token.json')
    return credential_path


def get_credentials():
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    #CLIENT_SECRET_FILE = 'client_secrets.json'
    REDIRECT_URI='urn:ietf:wg:oauth:2.0:oob'
    REFRESH_TOKEN = "refresh_token"
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.dashai')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'client_secret.json')
    flow = client.flow_from_clientsecrets(credential_path, SCOPES, REDIRECT_URI)
    flow.params['access_type'] = 'offline'
    flow.params['state'] = 'state-token'
    #flow.params['approval_prompt'] = 'force'
    auth_uri = flow.step1_get_authorize_url()
    #auth_uri = auth_uri+'&state=state-token&approval_prompt=force'
    print(auth_uri)
    auth_code = raw_input('Wait: ')
    webbrowser.open(auth_uri)
    auth_code = raw_input('Enter the auth code: ')
    credentials = flow.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())
    storage = Storage(os.path.join(credential_dir,'token-primary.json'))
    storage.put(credentials)
    credentials = storage.get()
    with open(os.path.join(credential_dir,'token-primary.json')) as data_file:
        data = json.load(data_file)
    token=(data['token_response'])
    now=datetime.now(tzlocal())+timedelta(hours=1)
    now_1hr=(now.isoformat())
    token['expiry'] = now_1hr
    token_path = os.path.join(credential_dir,'token.json')
    with open(token_path,'w') as outfile:
        json.dump(token,outfile)

def get_docID():
    print ("Please Open your Google Sheets in a browser and Copy the URL")
    print ("Example: https://docs.google.com/spreadsheets/d/1NnmdNxhBKQe9veBoWjptDCG2ZOOrOXkNV6yqMYP4meI/edit#gid=0")
    ans=raw_input("Paste URL here: ")
    url=ans.split("/")
    docId=url[5]
    print("Document ID is: "+ docId)
    return docId;

def sheets_secrets():
    print("Setting tokens as OC secrets")
    client_token_path=get_client_token()
    private_token_path=get_private_token()
    command = "oc delete secret sheets-tokens"
    call(command, shell=True)
    command = "oc create secret generic sheets-tokens --from-file=" + client_token_path +" --from-file=" + private_token_path + ""
    call(command, shell=True)
    command = "oc volume dc/sheets --add --type=secret --secret-name=sheets-tokens -m /go/src/app/"
    call(command, shell=True)

def launch_sheets(docId):
    command = "oc new-app https://github.com/alyarctiq/sheet-importer --name sheets -e DOC_ID='"+docId+"'"
    call(command, shell=True)
    print('\n')
    print('\n')
    print('Attaching Secrets')
    sheets_secrets()

def deploysheets():
      os.system('clear')
      print("Step 1 of 3 - Collect Sheets Document ID")
      raw_input("Press Enter to continue...")
      docId=get_docID()
      print("\n \n")
      print("Step 2 of 3 - Authorize DashAi")
      raw_input("Press Enter to continue...")
      get_credentials()
      print("\n \n")
      print("Step 3 of 3 - Launch DashAi Sheets Collector")
      raw_input("Press Enter to continue...")
      launch_sheets(docId)
      raw_input("Press Enter to continue...")
      os.system('clear')
      return;

def endpoints():
    os.system('clear')
    print('Current Endpoints')
    print('\n')
    command = "oc get routes"
    call(command, shell=True)
    raw_input("Press Enter to continue...")
    return;


def impoter_output(endpoint,db):
    outputblock="""
        [agent]
          interval = "10s"
          round_interval = true
          metric_batch_size = 1000
          metric_buffer_limit = 10000
          collection_jitter = "0s"
          flush_interval = "10s"
          flush_jitter = "0s"
          precision = ""
          logfile = ""
          hostname = ""
          omit_hostname = false

        [[outputs.influxdb]]
          urls = [\"%s\"] # required
          database = \"%s\"
          retention_policy = ""
          write_consistency = "any"
          timeout = "5s"
          # username = "telegraf"
          # password = "metricsmetricsmetricsmetrics"
          # user_agent = "telegraf"
          # udp_payload = 512
          ## Optional SSL Config
          # ssl_ca = "/etc/telegraf/ca.pem"
          # ssl_cert = "/etc/telegraf/cert.pem"
          # ssl_key = "/etc/telegraf/key.pem"
          ## Use SSL but skip chain & host verification
          # insecure_skip_verify = false
     """
    output=(outputblock % (endpoint, db))
    print (output)
    raw_input("Press Enter to continue...")
    return output;

ans=True
while ans:
    os.system('clear')
    print ("""
    Welcome To DashAi !!
    Use this tool to get you started with DashAi on OpenShift!
    Currently Supported Modules:

    0.Deploy Core
    1.Deploy Nagios [ Nagios / Gearman ]
    2.Deploy OpenShift Metric's Integration
    3.Deploy Jenkins Integration
    4.Deploy JIRA Integration
    5.Deploy Google Sheets Integration
    6.Apache
    7.Endpoints
    X.Exit/Quit
    """)

    ans=raw_input("What would you like to do? ")
    if ans=="0":
       deploycore()
    elif ans=="1":
       deploynagios()
    elif ans=="2":
       deployocp()
    elif ans=="3":
      deployjenkins()
    elif ans=="4":
      deployjira()
    elif ans=="5":
      deploysheets()
    elif ans=="6":
      impoter_output()
    elif ans=="7":
      endpoints()
    elif ans=="X":
      print(" Goodbye")
      #raw_input("Press Enter to continue...")
      os.system('clear')
      ans=False
    elif ans !="":
      print(" Not Valid Choice Try again")
