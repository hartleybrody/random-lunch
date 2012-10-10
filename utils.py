
from models import DEPARTMENTS, Lunch
import logging


def get_gravatar_from_email(email, size=30):

    import urllib, hashlib

    gravatar_url = "http://gravatar.com/avatar/"
    gravatar_url += hashlib.md5(email.lower()).hexdigest()
    gravatar_url += "?"
    gravatar_url += urllib.urlencode({
        's': size,
        'd': "mm",
    })
    return gravatar_url


def choose_partner(available_employees, this_employee):
    """
    logic that returns a partner (Employee) for the
    single Employee from the list of employees, or None
    """
    if len(available_employees) == 0:
        return None

    from random import choice

    # create list of departments
    depts = [d["slug"] for d in DEPARTMENTS]

    # seperate employees into departments
    pools = {dept: [e for e in available_employees if e.department == dept] for dept in depts}

    # choose a random department
    sanity_check = 0
    while True and sanity_check < 25:
        sanity_check += 1
        chosen_dept = choice(depts)
        if len(pools[chosen_dept]) == 0:
            continue  # must be employees in this department
        if chosen_dept == this_employee.department:
            continue  # must be a different department than this_employee's

        # alright, we've found a potential dept, now let's find an employee
        sanity_check_2 = 0
        while True and sanity_check_2 < 25:
            sanity_check_2 += 1
            potential_partner = choice(pools[chosen_dept])
            logging.info("attempting to see if %s and %s have eaten before" % (this_employee, potential_partner))
            have_these_two_been_matched_before = Lunch.all().filter("employees = ", this_employee).filter("employees = ", potential_partner).count()
            logging.info("result: %s" % (have_these_two_been_matched_before, ))
            if not have_these_two_been_matched_before:
                return potential_partner

    if sanity_check == 25:
        logging.warning("couldn't find a department to match %s from %s" % (this_employee, available_employees))
        return None


