from django.urls import path

from apps.office import views
from apps.office.autocomplete_views import WorkerAutocomplete

urlpatterns = [
    path('', views.home, name='home'),
    path('null', views.null, name='null'),
    path('worker-autocomplete', WorkerAutocomplete.as_view(), name='worker-autocomplete'),
    path('workers/<int:pk>', views.WorkerDetailView.as_view(), name='worker_details')
]
