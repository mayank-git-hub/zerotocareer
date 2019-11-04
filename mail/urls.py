from django.urls import path

from .views import *


app_name = 'mail'
urlpatterns = [
	path('test_mail/', test_mail, name='test_mail'),
	path('task_join_time_mail/', task_join_time_mail, name='task_join_time_mail'),
	path('queue_join_confirmation_mail/', queue_join_confirmation_mail, name='queue_join_confirmation_mail'),
	path('task_over_confirmation_mail/', task_over_confirmation_mail, name='task_over_confirmation_mail'),
]
