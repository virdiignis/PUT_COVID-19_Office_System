from django.urls import path

from apps.covid import views
from apps.covid.autocomplete_views import PersonAutocomplete, UnitAutocomplete

urlpatterns = [
    path('cases', views.CaseListView.as_view(), name='cases'),
    path('cases/<int:pk>/update', views.CaseUpdateView.as_view(), name='case_update'),
    path('cases/<int:pk>/close', views.case_close, name='case_close'),
    path('cases/<int:pk>/reopen', views.case_reopen, name='case_reopen'),
    path('cases/<int:pk>', views.CaseDetailView.as_view(), name='case_details'),
    path('cases/new', views.CaseCreateModalView.as_view(), name='case_new_modal'),
    path('person-autocomplete', PersonAutocomplete.as_view(), name='person-autocomplete'),
    path('person/new', views.PersonCreateModalView.as_view(), name='person_new_modal'),
    path('unit-autocomplete', UnitAutocomplete.as_view(), name='unit-autocomplete'),
    path('actions/<int:pk>', views.ActionDetailModalView.as_view(), name='action_details'),
    path('dashboard', views.covid_dashboard, name='covid_dashboard'),
    path('dashboard/actions/<int:page>', views.ActionDashboardView.as_view(), name='actions_dashboard'),
    path('dashboard/cases/<int:page>', views.CaseDashboardView.as_view(), name='cases_dashboard'),
    path('dashboard/isolations/<int:page>', views.IsolationDashboardView.as_view(), name='isolations_dashboard'),
    path('dashboard/isolationrooms/<int:page>', views.IsolationRoomDashboardView.as_view(),
         name='isolationrooms_dashboard'),
    path('actions', views.ActionListView.as_view(), name='actions'),
    path('actions/<int:pk>/based_on', views.action_contact_content, name='action_contact_content'),
    path('actions/<int:pk>/notes', views.action_notes, name='action_notes'),
    path('actions/new', views.ActionCreateModalView.as_view(), name='action_new_modal'),
]
