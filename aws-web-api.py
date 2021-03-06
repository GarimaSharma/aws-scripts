#!/usr/bin/env python
	
# author: Aditya Patawari <aditya@adityapatawari.com>

import sqlite3
import ConfigParser
import os.path
import boto
import web

url = (
  '/v1/up/(.+)', 'SpinInstance',
  '/v1/down/(.+)', 'StopInstance',
  '/v1/terminate/(.+)', 'TerminateInstance',
)

__author__ = "Aditya Patawari <aditya@adityapatawari.com>"

Description = '''
The format for the conf file (path of which is ~/.aws.conf) is : 
[AWS]
consumer_key: <Consumer Key>
consumer_secret: <Consumer Secret>
db_path: <SQLite path>
'''

class SpinInstance:
  check = os.path.isfile(os.path.expanduser('~/.aws'))
  if cmp(check,False) == 0:
    print Description	
    sys.exit(2)

  def GET(self,name):
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.aws.conf'))
    id = config.get("AWS", "access_key_id", raw=True)
    key = config.get("AWS", "secret_access_key", raw=True)
    db_path = config.get("AWS", "db_path", raw=True)
    
    sql_conn = sqlite3.connect(db_path)
    c = sql_conn.cursor()
    hostname = (name, ) 
    c.execute("select * from fleet where hostname=?",hostname)
    hostdata = c.fetchone()
    self.image_id = str(hostdata[0])
    self.key_name = str(hostdata[1])
    self.security_group_ids = str(hostdata[2]).split(',')
    self.user_data = str(hostdata[3])
    self.instance_type = str(hostdata[4])
    self.placement = str(hostdata[5])
    self.subnet_id = str(hostdata[6])
    self.private_ip_address = str(hostdata[7])
    self.public_ip_address = str(hostdata[8])
    self.hostname = str(hostdata[9])
    self.tags = str(hostdata[10])

    aws_conn = boto.connect_ec2(id, key)

    instance = aws_conn.run_instances(image_id=self.image_id,user_data=self.user_data, security_group_ids=self.security_group_ids, instance_type=self.instance_type,subnet_id=self.subnet_id,private_ip_address=self.private_ip_address)

    aws_conn.create_tags([str(instance.instances[0]).split(':')[1]],{'Name':self.tags})
    return "A box with hostname "+name+" is being processed"

app = web.application(url, globals())
if __name__ == '__main__':
  app.run()
