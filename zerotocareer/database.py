from pymongo import MongoClient

client = MongoClient()

# client.drop_database('zerotocareer')
# exit(1)
zerotocareer = client.zerotocareer

users = zerotocareer.users
active = zerotocareer.active
waiting = zerotocareer.waiting
dormant = zerotocareer.dormant
tasks = zerotocareer.tasks
accounts = zerotocareer.accounts

task_messages = zerotocareer.task_messages


def fill_dummy_messages(task_id):
	all_messages = {
		'0': {'mayank': 'Hello mayanksingh, how are you?'},
		'1': {'mayanksingh': 'Hey mayank! I am great. It is a pleasure being in this assignment with you!'},
		'2': {'mayank': 'Great! Lets start it!'},
		'3': {'mayank': 'First, lets break down each of our responsibilities!'},
		'4': {'mayanksingh': 'Umm, could you concnetrate on test case 1? I feel more confident in test case 2'},
		'5': {'mayank': 'Sure'},
		'6': {'mayanksingh': 'Mine is done!'},
		'7': {'mayank': 'mine is too'},
		'8': {'mayanksingh': 'Lets check out the results!'}
	}

	score = {
		'mayank': 0.4,
		'mayanksingh': 0.6,
	}

	task_messages.insert_one({'task_id': task_id, 'messages': all_messages, 'score': score})

# fill_dummy_messages('XATHONSOCEUELLGXGMXH')
