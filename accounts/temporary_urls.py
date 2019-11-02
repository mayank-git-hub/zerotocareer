from django.urls import path

from .views import *

app_name = 'mail'
urlpatterns = [
	path('', default_view, name='default_view'),
]
