from django.urls import path

from .views import *


app_name = 'mail'
urlpatterns = [
	path('test_mail/', test_mail, name='test_mail'),
]
