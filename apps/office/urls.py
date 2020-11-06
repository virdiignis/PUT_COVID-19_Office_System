from django.urls import path

from apps.office import views
from apps.office.autocomplete_views import WorkerAutocomplete

urlpatterns = [
    path('', views.home, name='home'),
    path('null', views.null, name='null'),
    path('worker-autocomplete', WorkerAutocomplete.as_view(), name='worker-autocomplete'),
    path('workers/<int:pk>', views.WorkerDetailView.as_view(), name='worker_details'),
    path('dashboard/reminders/<int:page>', views.ReminderDashboardView.as_view(), name='reminders_dashboard'),
    path('dashboard/reminders/mark_done/<int:pk>', views.reminder_mark_done, name='reminders_mark_done'),
    path('reminders/<int:page>', views.ReminderListView.as_view(), name='reminders'),
    path('reminders/new', views.ReminderCreateModalView.as_view(), name='reminder_new_modal'),
]
