from zerotocareer.database import active, tasks, dormant, accounts, users, waiting, task_messages
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import os
from datetime import datetime, timedelta
import threading
import random
import string
from zerotocareer.settings import task

from mail.views import task_join_time_mail, task_over_confirmation_mail
os.environ[
	"GOOGLE_APPLICATION_CREDENTIALS"] = "/home/Common/GitRepos/new/zerotocareer/My First Project-6d907488034a.json"

client = language.LanguageServiceClient()


def start_task():

	"""
	This function is called when the task starts after task['wait_time_seconds'} runs out
	:return:
	"""

	# Create user-password for the git repository

	for user in dormant.find():

		create_user_command = \
			"echo mayank1 | sudo -S htpasswd -b /home/git/GitRepos/htpasswd " + \
			str(user['user_id'] + ' ' + str(user['git_password']))

		# Created github id for user: user['user_id']
		os.system(create_user_command)

	# Creating root user who will be commiting the template code in the git repo
	create_root_command = "echo mayank1 | sudo -S htpasswd -b /home/git/GitRepos/htpasswd root root1"
	os.system(create_root_command)

	# Getting the task id
	task_id = tasks.find_one({'status': 'active'})['task_id']

	# Create Git Repository
	commands = """
			cd /home/git/GitRepos
			mkdir {0}.git
			cd {0}.git
			git --bare init
			git update-server-info
			echo mayank1 | sudo -S chown -R root.root .
			sudo chmod -R 777 .
		""".format(task_id)

	os.system(commands)

	# Copying the template code the repository and commiting it with the root credentials
	initialize_repo(task_id)

	# Shifting each user from dormant collection to active collection

	for user in dormant.find():
		dormant.delete_one({'user_id': user['user_id']})
		active.insert_one({'user_id': user['user_id']})

	return {'status': 'success', 'git_repo_name': '{0}.git'.format(task_id)}


def check_score(output, target):

	"""

	:param output: {'<test_case_id>': '<test_case_output>'}
	:param target: {'<test_case_id>': '<test_case_output>'}
	:return:
		{
			'num_pass': number of test cases passed,
			'pass': [True/False for each test case]
		}
	"""

	results = dict()
	results['num_pass'] = 0
	results['pass'] = {}

	for i in output.keys():
		if output[i] == target[i]:
			results['num_pass'] += 1
			results['pass'][i] = True
		else:
			results['pass'][i] = False

	return results


def initialize_repo(task_id):

	"""
	Calls the initialize_repo script which copies the template code and commits it under the root user
	:param task_id: task_id used as an identifier of the git repository
	:return:
	"""
	command = './engine/scripts/initialize_repo.sh {0}'.format(task_id)
	os.system(command)


def get_google_nlp_score(messages, user_list):

	"""
	Generated google nlp score and uses sentiment part of the score to rank the users
	:param messages:
		{
			'<message_number>': {'<user_name>': '<message>'},
		}
	:param user_list: list of all users
	:return:
		{
			'user_id': sentiment_score
		}
	"""
	all_text = ""
	score = dict()

	for user in user_list:

		for message_i in messages:
			if list(messages[message_i].keys())[0] == user:
				all_text += messages[message_i][user] + '\n'

		document = types.Document(
			content=all_text,
			type=enums.Document.Type.PLAIN_TEXT)

		# Detects the sentiment of the text
		sentiment = client.analyze_sentiment(document=document).document_sentiment

		score[user] = sentiment.score

	return score


def create_chat_score_per_user(message, user_list, task_id):

	"""
	Creates chat score per user using the google api
	Takes all the messages of the user and gets the sentiment score
	:param message:
		{
			'<message_number>': {'<user_name>': '<message>'},
		}
	:param user_list: [list of user_ids]
	:param task_id: current task_id
	:return:
		{
			'<user_id>': <score>
		}
	"""

	if 'score' not in message.keys():
		score = get_google_nlp_score(message['messages'], user_list)
		message['score'] = score
		task_messages.update_one({'task_id': task_id}, {"$set": message})

	average_score_per_user = dict()

	for user in user_list:
		average_score_per_user[user] = float(message['score'][user])

	return average_score_per_user


def create_code_score_per_user(results, task_id, test_case_map, user_list):
	"""
	:param results: {'num_pass': 0, 'pass': {'0': False, '1': False, '2': False, '3': False, '4': False, '5': False}}
	:parma task_id: BJDHZONLDKBDDHYDLDEO
	:parma test_case_map: {'0': '1', '1': '2', '2': '3', '3': '1', '4': '2', '5': '3'}
	:parma user_list: [list of all user_ids]
	:return:
		{
			'<user_id>': <code_score>
		}
	"""

	def get_contribution(unique_test_cases):
		"""
		Creates contribution of each
		:return:
		{
			'<test_function_id>': {'email_id': {'+': <num_lines_added>, '-': <num_lines_deleted>}}
		}
		"""

		base_dir = '/home/mayank/temporary_git_repos/'+task_id
		main_file = base_dir + '/main.py'

		template_command = "cd "+base_dir+";git log -L :test_case_{0}:"+main_file+" --pretty=fuller"

		# total_contribution would contain
		# {<'test_function_id'>: {'<email_id>': {'+': <num_insertion>, '-': <num_deletion>}}}
		total_contribution = {}

		for test_case_i in unique_test_cases:
			# iterating over each test_function

			# commit_messages would contain the time commited, author and commit_id
			commit_messages = os.popen("cd "+base_dir+";git log --follow -- "+main_file).read().split('\n')

			# Cleaning the commit_messages to get email_id of author and commit <commit_id>
			commit_messages = [[commit_messages[no + 1].split('<')[1].split('>')[0], _] for no, _ in enumerate(commit_messages) if _.startswith('commit')]

			# Further cleaning to remove (head ...)
			commit_messages = [[_[0], ' '.join(_[1].split()[0:2])] for _ in commit_messages]
			# Finally commit_messaged contains
			# [for all commits corresponding to the specific test_function [email_id, 'commit <commit_id>']]

			# output would contain the commit_id, author and number of lines inserted or deleted
			output = os.popen(template_command.format(test_case_i)).read().split('\n')

			# contribution would contain {'<email_id>': {'+': <num_insertion>, '-': <num_deletion>}}

			contribution = {}
			active = {'status': None, 'author': None}

			for output_i in output:
				if len(output_i) == 0:
					# Skipping blank lines
					continue
				if active['status'] is not None:
					# If active status is 'active' then update the insertion and deletion
					if output_i[0] == '+':
						contribution[active['author']]['+'] += 1
					elif output_i[0] == '-':
						contribution[active['author']]['-'] += 1

				for commit_message in commit_messages:
					if output_i.startswith(commit_message[1]):
						# If the line is a commit message then a new commit is starting so change the author
						active['status'] = 'active'
						active['author'] = commit_message[0]
						contribution[commit_message[0]] = {'+': 0, '-': 0}
						break

			total_contribution[str(test_case_i)] = contribution

		return total_contribution

	def get_unique_test_cases():

		"""
		Get test_case_function_ids
		:return: [1, 2, 3]
		"""

		val = [int(test_case_map[key]) for key in test_case_map.keys()]
		val = set(val)
		return list(val)

	# Get the test_function_ids
	unique_test_cases = get_unique_test_cases()

	# Get contribution of each user indexed by function_id
	contribution = get_contribution(unique_test_cases)

	# Mapping of email_id to user_id
	email_ids = {users.find_one({'user_id': user_id})['email_id']: user_id for user_id in user_list}

	# Will contain the score of all users indexed by user_id
	all_score = {user_id: 0 for user_id in user_list}

	# Will contain the score of all users indexed by function_id
	score_i = {str(test_case_i): {user_id: 0 for user_id in user_list} for test_case_i in unique_test_cases}

	# This code adds the number of insertions to the score if the test_case passed
	# subtracts the number of insertions to the score if the test_case failed to
	# generate the final score of each user
	# Also the score is normalized so that total number of lines do not affect the score

	for all_test_case_i in results['pass'].keys():
		if results['pass'][all_test_case_i]:
			factor = 1
		else:
			factor = -1

		current_contribution = contribution[test_case_map[all_test_case_i]]
		for email_id in current_contribution.keys():
			user = email_ids[email_id]
			score_i[test_case_map[all_test_case_i]][user] += factor*current_contribution[email_id]['+']

	total_user_scores = 0
	for all_test_case_i in results['pass'].keys():
		for user in user_list:
			all_score[user] += score_i[test_case_map[all_test_case_i]][user]/len(results['pass'].keys())
			total_user_scores += score_i[test_case_map[all_test_case_i]][user]/len(results['pass'].keys())

	total_score = 0
	for result_i in results['pass'].keys():
		if results['pass'][result_i]:
			total_score += 1
	total_score /= len(results['pass'].keys())
	for user in user_list:
		all_score[user] = all_score[user]/total_user_scores*total_score

	return all_score


def save_score_per_user(code_score, chat_score, user_list, task_id):

	"""
	Stores the score of the user for the task in accounts collection
	:param code_score: {'<user_id>': score}
	:param chat_score: {'<user_id>': score}
	:param user_list: [list of all users]
	:param task_id: current task_id
	:return: None
	"""

	for user in user_list:

		cur_account = accounts.find_one({'user_id': user})
		if not cur_account:
			accounts.insert_one(
				{'user_id': user, 'tasks': {task_id: {'code_score': code_score[user], 'chat_score': chat_score[user]}}})
		else:
			cur_account['tasks'][task_id] = {'code_score': code_score[user], 'chat_score': chat_score[user]}
			accounts.update_one({"user_id": user}, {"$set": cur_account})


def task_join_time():
	"""
	Function is automatically called when the last user is added to the queue
	:param request:
	:return:
	"""

	# Check if the queue is actually full, otherwise send error message
	if waiting.count_documents({}) == task['active_people']:

		# Create a new random task_id. The while loop ensures that the random task_id is unique
		while True:
			random_task_id = ''.join([random.choice(string.ascii_uppercase) for _ in range(20)])
			if tasks.find_one({'task_id': random_task_id}) is None:
				break

		# Schedule the time when the task starts. Can be configured in zerotocareer/settings
		scheduled_time = timedelta(0, task['wait_time_seconds']) + datetime.now()

		# Get the user_id and the email_id of the users waiting in the queue
		waiting_user_ids = []
		waiting_user_email_ids = []

		for user in waiting.find():
			waiting_user_ids.append(user['user_id'])
			waiting_user_email_ids.append(users.find_one({'user_id': user['user_id']})['email_id'])

		# In the tasks collection enter the current task_id with the task_information
		tasks.insert_one(
			{
				'task_id': random_task_id,
				'users': waiting_user_ids,
				'time': str(datetime.now()),
				'status': 'active'
			}
		)

		# Generate random password for each user
		passwords = [
			''.join([random.choice(string.ascii_uppercase) for _ in range(5)]) for _i in range(len(waiting_user_ids))]

		# Send an email to each user with their user_id and password
		message = task_join_time_mail(waiting_user_ids, waiting_user_email_ids, passwords, scheduled_time)

		if message != 'Success':
			return message

		# Shift the users from the waiting collection to the dormant collection

		for no_i, (user_id, email_id) in enumerate(zip(waiting_user_ids, waiting_user_email_ids)):

			waiting.delete_one({'user_id': user_id})
			dormant.insert_one({'user_id': user_id, 'git_password': passwords[no_i]})

		# The function start_task would run after task['wait_time_seconds']
		threading.Timer(task['wait_time_seconds'], start_task).start()
		return 'Success'

	else:
		return 'Error: Asked to send task_join_time_mail when the queue is not yet filled'


def task_over_confirmation():

	"""
	Cleanup commands after the task is over and sends email to each user with link to results
	:return: task_id
	"""

	# Get current task attributes
	cur_task = tasks.find_one({'status': 'active'})

	# Send the mail confirming that the task is over
	message = task_over_confirmation_mail(cur_task['users'], cur_task['task_id'])

	if message != 'Success':
		return message

	# Remove the users from the active collection
	for user_id in cur_task['users']:

		active.delete_one({'user_id': user_id})

	# Update the current task status
	cur_task['status'] = 'done'
	tasks.update_one({"status": 'active'}, {"$set": cur_task})

	# Remove the user_ids from git
	for user_id in cur_task['users']:
		delete_user_git_command = "echo mayank1 | sudo -S htpasswd -D /home/git/GitRepos/htpasswd {0}".format(user_id)
		os.system(delete_user_git_command)

	return cur_task['task_id']
