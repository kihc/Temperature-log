#-*- coding: utf-8 -*-

from models import NdbTemperatura
import webapp2, urllib2, logging
from HTMLParser import HTMLParser
from google.appengine.api import mail
from datetime import datetime, date
import jinja2
import os
import sys
import json
from google.appengine.api import mail
import xml.etree.ElementTree as ET
import helper
from google.appengine.ext import ndb


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


if helper.is_debug():
    server_url = "http://lannisport:3000/test"
else:
    server_url = "http://193.77.101.140:10001/test"

arso_url = "http://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observationAms_IDRIJA_CISTI-NAP_latest.xml"

notify_email_to = "miha.sedej@gmail.com"
notify_email_from = "miha.sedej@gmail.com"
notify_email_subject = "Obvestilo miha-random"



class IndexHandler(webapp2.RedirectHandler):
    def get(self):




        db_temperatura = NdbTemperatura.query(NdbTemperatura.date > datetime(2010, 4, 1)).fetch()
        db_temperatura = [i for i in db_temperatura if i.vlaga_arso > 0.0]


        json_temperatura = {
            'cols':
            [
                {'id': '', 'label': 't', 'type': 'date'},
                {'id': '', 'label': 'Temperatura:', 'type': 'number'},
                {'id': '', 'label': 'Zun. temp:', 'type': 'number'}
            ],
            'rows': []
        }

        json_vlaga = {
            'cols':
            [
                {'id': '', 'label': 't', 'type': 'date'},
                {'id': '', 'label': 'Vlaga:', 'type': 'number'},
                {'id': '', 'label': 'Zun. vlaga:', 'type': 'number'}
            ],
            'rows': []
        }


        #temperatura = "['time', 'Temperatura'],\n"
        #vlaga = "['time', 'Vlaga'],\n"
        for i in db_temperatura:
            #temperatura = temperatura + "['" + str(i.date) + "', " + str(i.temperatura) + "],\n"
            #temperatura = temperatura + "['" + str(i.date) + "', " + str(i.vlaga) + "],\n"

            datum = datetime.strptime(str(i.date), '%Y-%m-%d %H:%M:%S.%f')

            json_datum = "Date(" + str(datum.year) + ", " + str(datum.month-1) + ", " + str(datum.day) + ", "
            json_datum += str(datum.hour) + ", " + str(datum.minute) + ", " + str(datum.second) + ")"

            json_temperatura['rows'].append({'c': [{'v': json_datum}, {'v': str(i.temperatura)}, {'v': str(i.temperatura_arso)}]})
            json_vlaga['rows'].append({'c': [{'v': json_datum}, {'v': str(i.vlaga)}, {'v': str(i.vlaga_arso)}]})

        template_values = {
            'json_temperatura': json_temperatura,
            'json_vlaga': json_vlaga,
            'temperatura': db_temperatura[-1].temperatura,
            'vlaga': db_temperatura[-1].vlaga,
            'temperatura_arso': db_temperatura[-1].temperatura_arso,
            'vlaga_arso': db_temperatura[-1].vlaga_arso
        }

        template = jinja_environment.get_template('templates/glavna.htm')
        self.response.out.write(template.render(template_values))


class GetTempHandler(webapp2.RequestHandler):
    def get(self):
        try:
            result = urllib2.urlopen(server_url)
            result_splited = result.read().split(";")

            http_xml = urllib2.urlopen(arso_url)
            tree = ET.parse(http_xml)
            root = tree.getroot()

            """
            for valid in root.iter('valid'):
                self.response.out.write(valid.text)
            """

            t_arso = -274.0
            rh_arso = -274.0
            temp = -274.0
            hum = -274.0

            for t in root.iter('t'):
                t_arso =  round(float(t.text), 2)

            for rh in root.iter('rh'):
                rh_arso = round(float(rh.text), 2)

            temp = round(float(result_splited[0]), 2)
            hum = round(float(result_splited[1]), 2)

            dbTemperatura = NdbTemperatura()

            if temp != -274:
                dbTemperatura.temperatura = temp

            if hum != -274:
                dbTemperatura.vlaga = hum

            if t_arso != -274:
                dbTemperatura.temperatura_arso = t_arso

            if rh_arso != -274:
                dbTemperatura.vlaga_arso = rh_arso

            dbTemperatura.put()

            #print hum, temp

        except TypeError as e:
            #error_message = "TypeError: " + "\n" + e.errno + "\n" + e.strerror
            error_message = sys.exc_info()
            #error_message += "\n:" + str(t_arso) + "\n:" + str(rh_arso)

            notify_send_email(error_message)

        except:
            notify_send_email(sys.exc_info())

            #self.response.out.write(sys.exc_info())



def notify_send_email(body):
        message = mail.EmailMessage(sender=notify_email_from, subject=notify_email_subject)
        message.to = notify_email_to
        message.body = body
        message.send()

#ruter

app = webapp2.WSGIApplication([('/osvezi', GetTempHandler),
                               ('/', IndexHandler)],
                              debug=True)


