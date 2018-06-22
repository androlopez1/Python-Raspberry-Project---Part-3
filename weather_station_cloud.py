#!/usr/bin/python
import os
import time
from time import sleep, strftime, time 
from datetime import datetime
import smtplib
from email import Encoders
from email.MIMEBase import MIMEBase
from email.mime.multipart import MIMEMultipart
import sys
import Adafruit_DHT
import lcddriver
import csv
from firebase import firebase
import json

firebase = firebase.FirebaseApplication(YOUR URL HERE, None)

f_time = datetime.now().strftime('%a %d %b @ %H:%M')
toaddr = YOUR EMAIL HERE    # redacted
me = 'sensor@test.com' # redacted

msg = MIMEMultipart()
msg['From'] = me
msg['To'] = toaddr

#display = lcddriver.lcd()

while True:
  msg.set_payload([])
  humidity, temperature = Adafruit_DHT.read_retry(11, 17)
  print temperature, humidity
#  display.lcd_display_string("Temperatura: "+str(temperature), 1)
#  display.lcd_display_string("Humedad: "+str(humidity), 2)
  doc = open("data_2.csv","a")
  doc_static = open("data_static.csv","a")
  with doc, doc_static:
    fieldnames = ['hora', 'temperatura','humedad']
    writer = csv.DictWriter(doc, fieldnames=fieldnames)
    writer_static = csv.DictWriter(doc_static, fieldnames=fieldnames)
    writer.writerows([{'hora':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'temperatura':str(temperature),'humedad':str(humidity)}])
    writer_static.writerows([{'hora':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'temperatura':str(temperature),'humedad':str(humidity)}])
  doc.close()
  doc_static.close()
  current_time = datetime.now()
  data = {"Hora":str(current_time.strftime("%Y-%m-%d %H:%M:%S")),"Temperatura":temperature, "Humedad":humidity}
  sent = json.dumps(data)
  firebase.post("data", sent)
  sleep(60)
  print current_time.hour, current_time.minute
  if ((current_time.hour == 23  and current_time.minute == 59) or (current_time.hour == 6  and current_time.minute == 0) or (current_time.hour == 12 and current_time.minute == 00) or (current_time.hour == 18 and current_time.minute == 0)):
      try:
         data = MIMEBase('application',"octect-stream")
         data.set_payload(open('data_2.csv').read())
         Encoders.encode_base64(data)
         data.add_header('Content-Disposition','data',filename=os.path.split("data_2.csv")[1])
         subject = 'Data ' + f_time
         msg['Subject'] = subject
         msg.preamble = "Data @ " + f_time
         msg.attach(data)
         s = smtplib.SMTP("smtp.gmail.com", 587)
         s.starttls()
         s.login(user = 'YOUR EMAIL HERE', password = YOUR PASSWORD HERE)
         s.sendmail(me, toaddr, msg.as_string())
         s.quit()
         os.remove("data_2.csv")

      except:
         print ("Error: unable to send email")
  else:
    pass
