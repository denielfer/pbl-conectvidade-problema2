from django.urls import path
from django.conf.urls import url
from .views import home, add, remove

urlpatterns = [
    url("add/$", add, name = 'add'),
    url("remove/$", remove, name = 'remove'),
    path("", home, name = 'home'),
]