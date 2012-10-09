from google.appengine.ext import db
import logging

DEPARTMENTS = [
    {"name": "Product", "slug": "product"},
    {"name": "Sales", "slug": "sales"},
    {"name": "Marketing", "slug": "marketing"},
    {"name": "Support", "slug": "support"},
    {"name": "Services", "slug": "services"},
    {"name": "Finance", "slug": "finance"},
    {"name": "IT", "slug": "it"},
    {"name": "People Ops", "slug": "people-ops"},
    {"name": "Executives", "slug": "executive"},
]

("product", "sales", "marketing", "support", "services", "executive", "finance", "IT", "people ops")

class Employee(db.Model):
    """a hubspot employee who wants to meet people!"""
    user = db.UserProperty()
    signed_up = db.DateTimeProperty(auto_now_add=True)
    department = db.StringProperty(choices=[e["slug"] for e in DEPARTMENTS])

    def gravatar_url(self):
        import urllib, hashlib

        gravatar_url = "http://gravatar.com/avatar/"
        gravatar_url += hashlib.md5(self.reviewer.nickname().lower()).hexdigest()
        gravatar_url += "?"
        gravatar_url += urllib.urlencode({
            's':"300",
            'd':"mm", 
        })
        return gravatar_url

    def __repr__(self):
        return "E in %s" % self.department

class Lunch(db.Model):
    """a meeting of two employees"""
    employees = db.ListProperty(db.Key) # many-to-many relationship
    assigned = db.DateTimeProperty(auto_now_add=True)

    def __repr__(self):
        return "lunch with %s" % (self.employees)
