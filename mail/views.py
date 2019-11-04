from django.shortcuts import HttpResponse, redirect
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes

import sys
import random
import string
from zerotocareer.database import active, waiting, users, tasks
from zerotocareer.settings import task
from zerotocareer.common_classes import JSONOpenAPIRender
from datetime import datetime

# Create your views here.


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def test_mail(request):

	try:

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

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def task_join_time_mail(request):

	try:

		if not request.user.is_authenticated:
			redirect('/accounts/login')

		if waiting.count_documents({}) == task['active_people']:

			while True:
				random_task_id = ''.join([random.choice(string.ascii_uppercase) for i in range(20)])
				if tasks.find_one({'task_id': random_task_id}) is None:
					break

			scheduled_time = 0

			waiting_user_ids = []
			waiting_user_email_ids = []

			for user in waiting.find():
				waiting_user_ids.append(user['user_id'])
				waiting_user_email_ids.append(users.find_one({'user_id': user['user_id']})['email_id'])

			tasks.insert_one(
				{
					'task_id': random_task_id,
					'users': waiting_user_ids,
					'time': str(datetime.now()),
					'status': 'active'
				}
			)

			# Clean up waiting list and fill up active list

			for user_id, email_id in zip(waiting_user_ids, waiting_user_email_ids):

				password = ''.join([random.choice(string.ascii_uppercase) for i in range(5)])
				email = """
						Hello everyone!

						We are glad that you have waited patiently. 
						Your task is scheduled on {0}. 

						The link to the test portal is: {1}. Login using your respective credentials.

						Your git username is {2}
						Your git password is {3}

						And remember the most important part of the task, having fun!

						Cheers and All the Best!

						ZeroToCareer team.""".format(scheduled_time, task['portal'], user_id, password)

				send_mail(
					'Your Task is Scheduled: ZeroToCareer',
					email,
					settings.EMAIL_HOST_USER,
					[email_id]
				)

				waiting.delete_one({'user_id': user_id})

				active.insert_one({'user_id': user_id, 'git_password': password})

			return HttpResponse('Success: Email Sent')

		else:
			return HttpResponse('Error: Asked to send task_join_time_mail when the queue is not yet filled')

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def queue_join_confirmation_mail(request):

	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		print(users.find_one({'user_id': request.user.username}))

		email_id = users.find_one({'user_id': request.user.username})['email_id']

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

		waiting.insert_one({'user_id': request.user.username})

		return HttpResponse('Success: Email Sent')

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def task_over_confirmation_mail(request):

	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		cur_task = tasks.find_one({'status': 'active'})

		for user_id in cur_task['users']:

			email_id = users.find_one({'user_id': user_id})['email_id']

			message = """
						Hope you enjoyed the test! To have a look at your performance visit:{}0
			""".format(task['performance_url'])

			send_mail(
				'Added to the Queue: ZeroToCareer',
				message,
				settings.EMAIL_HOST_USER,
				[email_id],
				fail_silently=False,
			)

			active.delete_one({'user_id': user_id})

		cur_task['status'] = 'done'
		tasks.update_one({"status": 'active'}, {"$set": cur_task})

		return HttpResponse('Success: Email Sent')

	except:

		return HttpResponse(sys.exc_info())
