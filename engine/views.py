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

from zerotocareer.database import active, waiting, dormant, users, tasks, task_messages
from zerotocareer.common_classes import JSONOpenAPIRender
from zerotocareer.settings import task

from .helper_functions import start_task, check_score, create_code_score_per_user
from .helper_functions import create_chat_score_per_user, save_score_per_user

# Mails
from mail.views import task_over_confirmation_mail, queue_join_confirmation_mail, task_join_time_mail


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def status_checker(request):

	"""
	Might be useful for the UI to check what is the status of the task
	:param request:
	:return:
		waiting: User is currently in the queue
		active: User is currently completing the task
		dormant: Queue is full, user is waiting for the task to start
		none: User has not joined any task
	"""

	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	if waiting.fine_one({'user_id': request.user.username}):
		return HttpResponse('waiting')
	if active.fine_one({'user_id': request.user.username}):
		return HttpResponse('active')
	if dormant.fine_one({'user_id': request.user.username}):
		return HttpResponse('dormant')

	return HttpResponse('none')


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def queue_join_confirmation(request):

	"""
	API should be called when the user commits to the task.
	This function adds the user to the queue and if the queue is full
	:param request:
	:return:
		waiting: User is currently in the queue
		active: User is currently completing the task
		dormant: Queue is full, user is waiting for the task to start
		none: User has not joined any task
	"""

	try:

		if not request.user.is_authenticated:
			return redirect('/accounts/login')

		print(users.find_one({'user_id': request.user.username}))

		email_id = users.find_one({'user_id': request.user.username})['email_id']

		if waiting.count() == task['active_people'] - 1:
			waiting.insert_one({'user_id': request.user.username})
			return redirect('/engine/task_join_time')

		queue_join_confirmation_mail(email_id)

		waiting.insert_one({'user_id': request.user.username})

		return HttpResponse('Success')

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

	return render(request, 'engine/taskpage.html', {'task_id': tasks.find_one({'status': 'active'})['task_id']})

	# except:
	# 	return HttpResponse('Error')


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def check_test_case(request):
	if not request.user.is_authenticated:
		return redirect('/accounts/login')

	task_id = tasks.find_one({'status': 'active'})['task_id']
	os.system('bash ./engine/scripts/test_script.sh {0} {1}'.format(task_id, task_id))
	with open('/home/mayank/temporary_files/'+task_id+'_', 'r') as f:
		output = json.load(f)
		target = {'0': '3', '1': '1', '2': '8'}
		results = check_score(output, target)
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
	cur_task = tasks.find_one({'status': 'active'})
	task_id = cur_task['task_id']
	users = cur_task['users']
	message = task_messages.find_one({'task_id': task_id})
	os.system('bash ./engine/scripts/final_test_script.sh {0} {1}'.format(task_id, task_id))
	with open('/home/mayank/temporary_files/' + task_id + '_final', 'r') as f:
		output = json.load(f)

	target = {'0': '5', '1': '16', '2': '15625', '3': '15', '4': '25', '5': '625'}
	test_case_map = {'0': '1', '1': '2', '2': '3', '3': '1', '4': '2', '5': '3'}
	results = check_score(output, target)

	code_score = create_code_score_per_user(results, task_id, test_case_map)
	code_score = {'mayank': 0.2, 'mayanksingh': 1}
	chat_score = create_chat_score_per_user(message, users)
	save_score_per_user(code_score, chat_score, users, task_id)
	return redirect('/engine/task_over_confirmation')


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def task_over_confirmation(request):

	if not request.user.is_authenticated:
		return redirect('/accounts/login')
	print(tasks)
	cur_task = tasks.find_one({'status': 'active'})

	message = task_over_confirmation_mail(cur_task['users'], cur_task['task_id'])

	if message != 'Success':
		return HttpResponse(message)

	for user_id in cur_task['users']:

		active.delete_one({'user_id': user_id})

	cur_task['status'] = 'done'
	tasks.update_one({"status": 'active'}, {"$set": cur_task})

	for user_id in cur_task['users']:
		delete_user_git_command = "echo mayank1 | sudo -S htpasswd -D /home/git/GitRepos/htpasswd {0}".format(user_id)
		os.system(delete_user_git_command)

	return redirect('/accounts/profile/results?task_id={0}'.format(cur_task['task_id']))
