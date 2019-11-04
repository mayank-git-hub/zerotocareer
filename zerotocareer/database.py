from pymongo import MongoClient

client = MongoClient()

# client.drop_database('zerotocareer')
# exit(1)
zerotocareer = client.zerotocareer

users = zerotocareer.users
active = zerotocareer.active
waiting = zerotocareer.waiting
tasks = zerotocareer.tasks
