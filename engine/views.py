from django.shortcuts import redirect, HttpResponse, render
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes

import random
import string
import sys
import os
import json
from datetime import datetime, timedelta
import threading

from zerotocareer.database import active, waiting, dormant, users, tasks
from zerotocareer.common_classes import JSONOpenAPIRender
from zerotocareer.settings import task
# Create your views here.

from .helper_functions import start_task

# Mails
from mail.views import task_over_confirmation_mail, queue_join_confirmation_mail, task_join_time_mail


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def status_checker(request):

	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		if waiting.fine_one({'user_id': request.user.username}):
			return HttpResponse('Waiting')
		if active.fine_one({'user_id': request.user.username}):
			return HttpResponse('active')
		if dormant.fine_one({'user_id': request.user.username}):
			return HttpResponse('dormant')

		return HttpResponse('user not joined to any task')

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def queue_join_confirmation(request):

	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		print(users.find_one({'user_id': request.user.username}))

		email_id = users.find_one({'user_id': request.user.username})['email_id']

		queue_join_confirmation_mail(email_id)

		waiting.insert_one({'user_id': request.user.username})

		return HttpResponse('Success: Email Sent')

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def task_join_time(request):

	try:

		if not request.user.is_authenticated:
			redirect('/accounts/login')

		if waiting.count_documents({}) == task['active_people']:

			while True:
				random_task_id = ''.join([random.choice(string.ascii_uppercase) for _ in range(20)])
				if tasks.find_one({'task_id': random_task_id}) is None:
					break

			scheduled_time = timedelta(0, task['wait_time_seconds']) + datetime.now()

			threading.Timer(task['wait_time_seconds'], start_task).start()

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

			passwords = [
				''.join([random.choice(string.ascii_uppercase) for _ in range(5)]) for _i in range(len(waiting_user_ids))]

			message = task_join_time_mail(waiting_user_ids, waiting_user_email_ids, passwords, scheduled_time)

			if message != 'Success':
				return HttpResponse(message)

			for no_i, (user_id, email_id) in enumerate(zip(waiting_user_ids, waiting_user_email_ids)):

				waiting.delete_one({'user_id': user_id})

				dormant.insert_one({'user_id': user_id, 'git_password': passwords[no_i]})

			return HttpResponse('Success')

		else:
			return HttpResponse('Error: Asked to send task_join_time_mail when the queue is not yet filled')

	except:
		return HttpResponse(sys.exc_info())


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def taskpage(request):

	# try:
	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	if not active.find_one({'user_id': request.user.username}):
		return HttpResponse('Not started yet')

	return render(request, 'engine/taskpage')

	# except:
	# 	return HttpResponse('Error')


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def check_test_case(request):
	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	os.system('Run the testing script in the specific git folder')
	with open('output.txt', 'r') as f:
		output = f.read()
		target = {0: 'Expected Output'}
		results = check_test_case(output, target)
		num_pass = results['num_pass']
		if num_pass == len(target):
			return HttpResponse(json.dumps({'status': 'Success', 'output': output, 'num_pass': num_pass}))
		else:
			return HttpResponse(json.dumps({'status': 'Error', 'output': output, 'num_pass': num_pass}))


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def check_final_submission(request):
	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	os.system('Run the final script in the specific git folder')
	with open('output_final.txt', 'r') as f:
		output = f.read()
		target = {0: 'Expected Output'}
		results = check_test_case(output, target)

		# ToDo - this should take the pass_results and the git repo and compute score per user
		# code_score = create_score_per_user(pass_results)
		# ToDo - this should take the chatbot results and compute score per user
		# chat_score = create_chat_score_per_user(pass_results)
		# ToDo - this should store the generated results
		# save_score_per_user(code_score, chat_score)
		# ToDo - redirect the person to results page and put appropriate task id
		# ToDo - remove active users from active database to done database

		return redirect('/accounts/profile/results?task_id=task_id')


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def task_over_confirmation(request):
	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		cur_task = tasks.find_one({'status': 'active'})

		message = task_over_confirmation_mail(cur_task['users'])

		if message != 'Success':
			return HttpResponse(message)

		for user_id in cur_task['users']:

			active.delete_one({'user_id': user_id})

		cur_task['status'] = 'done'
		tasks.update_one({"status": 'active'}, {"$set": cur_task})

		# ToDo - Remove git user too or just change the password

		return HttpResponse('Success')

	except:

		return HttpResponse(sys.exc_info())

