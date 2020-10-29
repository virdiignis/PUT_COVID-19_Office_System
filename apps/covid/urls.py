from django.urls import path

from apps.covid import views

urlpatterns = [
    path('cases', views.CaseListView.as_view(), name='cases'),
    path('cases/<int:pk>', views.CaseDetailView.as_view(), name='case_details'),
]
