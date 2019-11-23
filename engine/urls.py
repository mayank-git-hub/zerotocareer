from django.urls import path

from .views import *

app_name = 'engine'

urlpatterns = [
	path('queue_join_confirmation', queue_join_confirmation, name='queue_join_confirmation'),
	path('check_final_submission', check_final_submission, name='check_final_submission'),
	path('check_test_case', check_test_case, name='check_test_case'),
	path('taskpage', taskpage, name='taskpage'),
	path('status_checker', status_checker, name='status_checker')
]
