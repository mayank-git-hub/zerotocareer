from pymongo import MongoClient

client = MongoClient()

zerotocareer = client.zerotocareer

users = zerotocareer.users
active = zerotocareer.active
waiting = zerotocareer.waiting
tasks = zerotocareer.tasks
