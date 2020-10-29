from django.urls import path

from apps.office import views

urlpatterns = [
    path('', views.home, name='home'),
]
