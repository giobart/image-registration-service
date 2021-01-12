import os

username = str(os.environ.get('MONGO_DB_USERNAME'))
password = str(os.environ.get('MONGO_DB_PASSWORD'))
print("Login credential: ", username)
