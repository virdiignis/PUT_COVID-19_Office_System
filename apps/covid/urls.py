from django.urls import path

from apps.covid import views
from apps.covid.autocomplete_views import PersonAutocomplete

urlpatterns = [
    path('cases', views.CaseListView.as_view(), name='cases'),
    path('cases/<int:pk>/update', views.CaseUpdateView.as_view(), name='case_update'),
    path('cases/<int:pk>/close', views.case_close, name='case_close'),
    path('cases/<int:pk>/reopen', views.case_reopen, name='case_reopen'),
    path('cases/<int:pk>', views.CaseDetailView.as_view(), name='case_details'),
    path('cases/new', views.CaseCreateModalView.as_view(), name='case_new_modal'),
    path('person-autocomplete', PersonAutocomplete.as_view(), name='person-autocomplete'),
    path('person/new', views.PersonCreateModalView.as_view(), name='person_new_modal'),
]

