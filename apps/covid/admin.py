from django.contrib.admin import AdminSite

from .models import *


class CovidAdminSite(AdminSite):
    site_header = "COVID Management Administrative Access"
    site_title = "PUT COVID-19 Office System"
    index_title = "PUT COVID-19 Office System"


covid_admin_site = CovidAdminSite(name='covid_admin')
covid_admin_site.register(Unit)
covid_admin_site.register(HealthState)
covid_admin_site.register(IsolationIssuer)
covid_admin_site.register(IsolationCause)
covid_admin_site.register(Person)
covid_admin_site.register(Case)
covid_admin_site.register(Isolation)
covid_admin_site.register(Action)
covid_admin_site.register(Document)
covid_admin_site.register(IsolationRoom)
