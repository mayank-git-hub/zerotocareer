import os
from zerotocareer.database import active, tasks, dormant, accounts
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
os.environ[
	"GOOGLE_APPLICATION_CREDENTIALS"] = "/home/Common/GitRepos/new/zerotocareer/My First Project-6d907488034a.json"

client = language.LanguageServiceClient()


def start_task():

	# Create user-password

	for user in dormant.find():

		create_user_command = \
			"echo mayank1 | sudo -S htpasswd -b /home/git/GitRepos/htpasswd " + \
			str(user['user_id'] + ' ' + str(user['git_password']))

		print('Created github id for user:', user['user_id'])

		os.system(create_user_command)

	create_root_command = "echo mayank1 | sudo -S htpasswd -b /home/git/GitRepos/htpasswd root root1"
	os.system(create_root_command)
	# Create Git Repository

	task_id = tasks.find_one({'status': 'active'})['task_id']

	print('Debug: task_id: {0}'.format(task_id))

	commands = """
			cd /home/git/GitRepos
			mkdir {0}.git
			cd {0}.git
			git --bare init
			git update-server-info
			echo mayank1 | sudo -S chown -R root.root .
			sudo chmod -R 777 .
		""".format(task_id)

	# commands = """
	# 		cd /home/git/GitRepos
	# 		echo mayank1 | sudo -S mkdir {0}.git
	# 		cd {0}.git
	# 		sudo git --bare init
	# 		sudo git update-server-info
	# 		sudo chown -R root.root .
	# 		sudo chmod -R 755 .
	# 	""".format(task_id)

	os.system(commands)

	initialize_repo(task_id)

	for user in dormant.find():
		dormant.delete_one({'user_id': user['user_id']})
		active.insert_one({'user_id': user['user_id']})

	return {'status': 'success', 'git_repo_name': '{0}.git'.format(task_id)}


def check_score(output, target):

	results = dict()
	results['num_pass'] = 0
	results['pass'] = {}

	print(output, target)

	for i in output.keys():
		if output[i] == target[i]:
			results['num_pass'] += 1
			results['pass'][i] = True
		else:
			results['pass'][i] = False

	return results


def initialize_repo(task_id):

	command = './engine/scripts/initialize_repo.sh {0}'.format(task_id)
	os.system(command)


def get_google_nlp_score(messages, users):

	# The text to analyze
	all_text = ""
	score = dict()

	for user in users:

		for message_i in messages:
			if messages[message_i].keys()[0] == user:
				all_text += messages[message_i][user] + '\n'

		document = types.Document(
			content=text,
			type=enums.Document.Type.PLAIN_TEXT)

		# Detects the sentiment of the text
		sentiment = client.analyze_sentiment(document=document).document_sentiment

		score[user] = sentiment.score

	return score


def create_chat_score_per_user(message, users):

	if 'score' not in message.keys():
		score = get_google_nlp_score(message['message'], users)
		message['score'] = score

	average_score_per_user = dict()

	for user in users:
		average_score_per_user[user] = float(message['score'][user])

	return average_score_per_user


def create_code_score_per_user(results, task_id, test_case_map):

	def get_line_mapping(all_code, unique_test_cases):

		template_prefix_line = 'def test_case_'
		mapping = {}

		num_ends_not_found = 0
		for test_case_i in unique_test_cases:
			cur_prefix = template_prefix_line + test_case_i
			start = None
			end = None

			for no, line in enumerate(all_code):
				if line.starswith(cur_prefix):
					start = no
					continue
				if line.starswith(template_prefix_line):
					end = no
					break
			if end is None:
				num_ends_not_found += 1
				end = len(all_code) - 1

			if start is None:
				raise ValueError("did not find the test_case_function")

			mapping[test_case_i] = {'start': start, 'end': end}

		if num_ends_not_found != 1:
			raise ValueError("Found multiple end not None")

		return mapping

	def get_code(task_id):

		base_dir = '/home/mayank/temporary_git_repos/'+task_id
		main_file = base_dir + '/main.py'

		with open(main_file, 'r') as f:
			return [i[:-1] for i in list(f)]

	def get_unique_test_cases():

		val = [int(test_case_map[key]) for key in test_case_map.keys()]
		val = set(val)
		return list(val)

	"""
	results: {'num_pass': 0, 'pass': {'0': False, '1': False, '2': False, '3': False, '4': False, '5': False}}
	task_id: BJDHZONLDKBDDHYDLDEO
	test_case_map: {'0': '1', '1': '2', '2': '3', '3': '1', '4': '2', '5': '3'}
	"""
	unique_test_cases = get_unique_test_cases()
	all_code = get_code(task_id)
	mapping_lines = get_line_mapping(all_code, unique_test_cases)
	# ToDo - this should take the pass_results and the git repo and compute score per user
	print(results, task_id, test_case_map)

	return {'mayank': 0.2, 'mayanksingh': 0.4}


def save_score_per_user(code_score, chat_score, users, task_id):

	for user in users:

		cur_account = accounts.find_one({'user_id': user})
		if not cur_account:
			accounts.insert_one(
				{'user_id': user, 'tasks': {task_id: {'code_score': code_score[user], 'chat_score': chat_score[user]}}})
		else:
			cur_account['tasks'][task_id] = {'code_score': code_score[user], 'chat_score': chat_score[user]}
			accounts.update_one({"user_id": user}, {"$set": cur_account})
