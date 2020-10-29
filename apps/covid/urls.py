from django.urls import path

from apps.covid import views

urlpatterns = [
    path('cases', views.CaseListView.as_view(), name='cases'),
]
