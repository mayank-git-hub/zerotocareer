from django.urls import path

from .views import *

app_name = 'engine'

urlpatterns = [
	path('start_task', start_task, name='start_task')
]
