from django.contrib.admin import AdminSite

from .models import *


class OfficeAdminSite(AdminSite):
    site_header = 'Office Administrative Access'
    site_title = "PUT COVID-19 Office System"
    index_title = "PUT COVID-19 Office System"


office_admin_site = OfficeAdminSite(name='office_admin')
office_admin_site.register(Worker)
office_admin_site.register(Reminder)
