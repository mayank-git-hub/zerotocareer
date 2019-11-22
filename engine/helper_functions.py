import os
from zerotocareer.database import active, tasks, dormant


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
		echo mayank1 | sudo -S mkdir {0}.git
		cd {0}.git
		sudo git --bare init
		sudo git update-server-info
		sudo chown -R root.root .
		sudo chmod -R 755 .
	""".format(task_id)

	os.system(commands)

	initialize_repo(task_id)

	for user in dormant.find():
		dormant.delete_one({'user_id': user['user_id']})
		active.insert_one({'user_id': user['user_id']})

	return {'status': 'success', 'git_repo_name': '{0}.git'.format(task_id)}


def check_test_case(output, target):

	results = dict()
	results['num_pass'] = 0

	for i in range(len(output)):
		if output[i] == target[i]:
			results['num_pass'] += 1

	return results


def initialize_repo(task_id):

	command = './engine/scripts/initialize_repo.sh {0}'.format(task_id)
	os.system(command)
