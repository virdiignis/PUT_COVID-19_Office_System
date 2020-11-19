from django.urls import path
from apps.forms import views

urlpatterns = [
    path('', views.forms, name='home'),
]
