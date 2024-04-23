import datetime
import subprocess
import pika
import socket
from time import sleep

def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()

def action(mac):
  
  printout = str(system_call("vcgencmd measure_temp"))[7:].split("'")[0]
  
  result = []
  result.append(printout)
  print(result)
  temps = []
  spots = ["CPU"]
  for i in range(len(spots)):
    entry = {}
    entry["Temperature"] = float(result[i])
    entry["PartName"] = spots[i]
    temps.append(entry)
  outbound = {}
  outbound["HostName"] = mac
  outbound["Timestamp"] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
  outbound["Temperatures"] = temps
  print(outbound)
  credentials = pika.PlainCredentials(os.environ["user"],os.environ["pass"])
  connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit.centurionx.net',5672,'/',credentials))
  channel = connection.channel()
  channel.basic_publish(exchange='InterTopic',
                      routing_key='temperature.node',
                      body=str(outbound))
  connection.close()


mac = system_call("ifconfig eth0 | grep -Eo ..\(\:..\){5}")[:-1].decode("utf-8")

while(True):
    action(mac)
    sleep(60)
