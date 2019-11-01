from pymongo import MongoClient

client = MongoClient()

users = client.user_level_db
user_info = users.user_info
email_ids = users.email_ids

users_click_history = client.user_click_history_db
users_history = users_click_history.users_history
