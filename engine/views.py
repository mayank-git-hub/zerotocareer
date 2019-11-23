from django.shortcuts import redirect, HttpResponse, render
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes
from django.contrib.auth.decorators import login_required

import os
import json


from zerotocareer.database import active, waiting, dormant, users, tasks, task_messages
from zerotocareer.common_classes import JSONOpenAPIRender
from zerotocareer.settings import task

from .helper_functions import check_score, create_code_score_per_user
from .helper_functions import create_chat_score_per_user, save_score_per_user, task_join_time
from .helper_functions import task_over_confirmation
# Mails
from mail.views import queue_join_confirmation_mail


@login_required
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

	if waiting.find_one({'user_id': request.user.username}):
		return HttpResponse('waiting')
	if active.find_one({'user_id': request.user.username}):
		return HttpResponse('active')
	if dormant.find_one({'user_id': request.user.username}):
		return HttpResponse('dormant')

	return HttpResponse('none')


@login_required
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

	# If same user tries to get into the queue twice then a message is displayed
	if waiting.find_one({'user_id': request.user.username}):
		return render(request, 'engine/queue_patience.html')

	if active.find_one({'user_id': request.user.username}):
		return redirect('/engine/taskpage')

	email_id = users.find_one({'user_id': request.user.username})['email_id']

	if waiting.count() == task['active_people'] - 1:

		# If the queue becomes full, sending email to everyone the task_join_time
		# Also shifting everyone from the waiting collection to the dormant collection

		waiting.insert_one({'user_id': request.user.username})
		message = task_join_time()

		return redirect('/engine/taskpage')

	# If the queue is not yet full, send a queue join confirmation mail to the user
	# The last user does not get this mail but directly gets the task_join_time mail
	queue_join_confirmation_mail(email_id)

	# Inserting the waiting users to the waiting collection
	waiting.insert_one({'user_id': request.user.username})

	return render(request, 'engine/queue_join.html')


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def taskpage(request):

	"""
	Temporary page request, should be designed and status can be found using /engine/status_checker
	:param request:
	:return:
	"""

	if not active.find_one({'user_id': request.user.username}):
		return render(request, 'engine/taskpage_notstarted.html')

	return render(request, 'engine/taskpage.html', {'task_id': tasks.find_one({'status': 'active'})['task_id']})


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def check_test_case(request):

	"""
	API used for checking the basic test cases.
	:param request:
	:return: {
				'status': 'Success/Error',
				'output': {'<test_case_id>': '<test_case_result>'},
				'num_pass': <num_test_cases_passed>
			}
	"""

	# Getting the task_id
	task_id = tasks.find_one({'status': 'active'})['task_id']

	# Running the test script on the git repo identified by the task_id
	# Storing the output in /home/mayank/temporary_files/<task_id>_
	# The test script's path is /engine/scripts/test_script.sh
	os.system('bash ./engine/scripts/test_script.sh {0} {1}'.format(task_id, task_id))

	with open('/home/mayank/temporary_files/'+task_id+'_', 'r') as f:

		# Loaded the stored json output
		output = json.load(f)

		# Hard coded targets
		target = {'0': '3', '1': '1', '2': '8'}

		# Calculating the results
		results = check_score(output, target)
		num_pass = results['num_pass']

		if num_pass == len(target):
			return HttpResponse(json.dumps({'status': 'Success', 'output': output, 'num_pass': num_pass}))
		else:
			return HttpResponse(json.dumps({'status': 'Error', 'output': output, 'num_pass': num_pass}))


@login_required
@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer, JSONOpenAPIRender])
def check_final_submission(request):
	"""
	API used for the final submission.
	:param request:
	:return: redicrects to the results page which should be designed.
	"""

	# Getting the task_id
	cur_task = tasks.find_one({'status': 'active'})
	task_id = cur_task['task_id']
	users = cur_task['users']
	message = task_messages.find_one({'task_id': task_id})

	# Running the final test script on the git repo identified by the task_id
	# Storing the output in /home/mayank/temporary_files/<task_id>_final
	# The final test script's path is /engine/scripts/final_test_script.sh
	os.system('bash ./engine/scripts/final_test_script.sh {0} {1}'.format(task_id, task_id))

	with open('/home/mayank/temporary_files/' + task_id + '_final', 'r') as f:
		output = json.load(f)

	# Hard coded targets
	target = {'0': '5', '1': '16', '2': '15625', '3': '15', '4': '25', '5': '625'}

	# Mapping of test_case to the test_case_functions
	test_case_map = {'0': '1', '1': '2', '2': '3', '3': '1', '4': '2', '5': '3'}

	# Calculating the results
	results = check_score(output, target)

	# Creates code score based on number of lines written by each user * score of the particular function
	code_score = create_code_score_per_user(results, task_id, test_case_map, users)
	# Creates chat score based on sentiment analysis of the chat
	chat_score = create_chat_score_per_user(message, users, task_id)
	# Saves the score in accounts collection
	save_score_per_user(code_score, chat_score, users, task_id)
	# Sends the mail that the task is over with the link to view the results
	task_over_confirmation()

	# ToDo - create the template
	return redirect('/accounts/profile/results?task_id={0}'.format(task_id))

