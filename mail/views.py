from django.shortcuts import HttpResponse, redirect
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes

import sys
from zerotocareer.settings import task
from zerotocareer.common_classes import JSONOpenAPIRender
from zerotocareer.database import users

# Create your views here.


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def test_mail(request):

	"""
	To test if the mail system is working! Edit the test_email_id in the code
	:param request:
	:return:
	"""

	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	send_mail(
		'Subject here',
		'Here is the message.',
		settings.EMAIL_HOST_USER,
		['mayank25031998@gmail.com'],
		fail_silently=False,
	)

	return HttpResponse('Success: Email Sent')


def task_join_time_mail(waiting_user_ids, waiting_user_email_ids, passwords, scheduled_time):


	for no_i, (user_id, email_id) in enumerate(zip(waiting_user_ids, waiting_user_email_ids)):

		email = """
	Hello everyone!

	We are glad that you have waited patiently. 
	Your task is scheduled on {0}. 

	The link to the test portal is: {1}. Login using your respective credentials.

	Your git username is {2}
	Your git password is {3}

	And remember the most important part of the task, having fun!

	Cheers and All the Best!

	ZeroToCareer team.
			""".format(scheduled_time, task['portal'], user_id, passwords[no_i])

		send_mail(
			'Your Task is Scheduled: ZeroToCareer',
			email,
			settings.EMAIL_HOST_USER,
			[email_id]
		)

	return 'Success'


def queue_join_confirmation_mail(email_id):

	message = """
	You have been added to the queue! 
	Please Be patient, we will send you an email when everyone is added with a link to the task portal. 
			"""

	send_mail(
		'Added to the Queue: ZeroToCareer',
		message,
		settings.EMAIL_HOST_USER,
		[email_id],
		fail_silently=False,
	)
	return 'Success'


def task_over_confirmation_mail(user_list, task_id):

	for user_id in user_list:

		email_id = users.find_one({'user_id': user_id})['email_id']

		message = """
	Hope you enjoyed the test! To have a look at your performance visit:
	http://dev.zerotocareer.com/accounts/profile/results?task_id={0}
		""".format(task_id)

		send_mail(
			'Added to the Queue: ZeroToCareer',
			message,
			settings.EMAIL_HOST_USER,
			[email_id],
			fail_silently=False,
		)

	return 'Success'
