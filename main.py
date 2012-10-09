#!/usr/bin/env python

import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import users, mail

from models import Employee, Lunch, DEPARTMENTS
from utils import get_gravatar_from_email, choose_partner

from datetime import datetime
import logging

class EmployeeHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            "user":     users.get_current_user(), 
            "gravatar": get_gravatar_from_email(users.get_current_user().nickname(), 40), 
            "departments": DEPARTMENTS, 
            "employee_count": Employee.all().count(),
        }
        self.response.out.write(template.render("templates/employee.html", template_values))

    def post(self):
        dept = self.request.get("department")
        user = users.get_current_user()

        e = Employee(user=user, department=dept)
        e.put()

        mail.send_mail(sender="Random Lunch <random-lunch@hubspot.com>",
              to=user.nickname(),
              subject="Get Ready to Meet HubSpotters",
              body="Thanks! You'll get an email soon matching you up with your first lunch date.")

        self.redirect("/thanks/")

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        self.response.out.write(template.render("templates/thanks.html", template_values))

class LunchHandler(webapp2.RequestHandler):
    def get(self, timeframe):

        current_user = users.get_current_user()
        template_values = {}

        if timeframe == "week":
            template_values["lunch"] = Lunch.all().filter("employees = ", current_user).order("-assigned")[0]

        elif timeframe == "month":
            template_values["lunch"] = Lunch.all().filter("employees = ", current_user).order("-assigned")[:4]

        else:
            self.error(404)
            return self.response.out.write("I don't know what timeframe you're trying to access...")

        self.response.out.write(template.render("templates/lunch.html", template_values))    

class ShuffleHandler(webapp2.RequestHandler):
    def get(self):
        key = self.request.get("key", False)
        if not key or key != "hartley-rulez":
            self.error(401)
            return self.response.out.write("What's the magic password??")

        # commence shufflin' http://youtu.be/KQ6zr6kCPj8
        all_employees = [e for e in Employee.all()] # lists are easier to work w than Query objects
        already_matched_employees = []
        created_lunches = []

        for employee in all_employees:
            if employee not in already_matched_employees:

                already_matched_employees.append(employee)
                employees_left = [e for e in all_employees if e not in already_matched_employees]
                partner = choose_partner(employees_left, employee)
                if partner:
                    logging.info("creating lunch between %s and %s" % (employee, partner))
                    already_matched_employees.append(partner)
                    l = Lunch(employees=[employee.key(), partner.key()])
                    l.put()
                    created_lunches.append(l)
                else:
                    logging.info("couldn't find lunch mate for %s" % employee)
                    already_matched_employees.remove(employee)

        logging.info("created lunches:")
        logging.info(created_lunches)





app = webapp2.WSGIApplication([
    ('/',                   EmployeeHandler),
    ('/thanks/',            ThanksHandler),
    ('/this/(\w+)/',        LunchHandler),
    ('/shuffle/',           ShuffleHandler),
], debug=True)


def main():
    # App Engine reuses your request handlers when you specify a main function
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(app)   

if __name__ == '__main__':
    main()