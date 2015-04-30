__author__ = 'Miha'

from google.appengine.ext import ndb


class NdbTemperatura(ndb.Model):
    temperatura = ndb.FloatProperty()
    vlaga = ndb.FloatProperty()
    temperatura_arso = ndb.FloatProperty()
    vlaga_arso = ndb.FloatProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_temperatura(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)

