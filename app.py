from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from bson import ObjectId
import pymongo
import datetime

# load in the variable in the .env file into our operating system environment
load_dotenv()

app = Flask(__name__)

# connect to Mongo
MONGO_URI = os.environ.get('MONGO_URL')
client = pymongo.MongoClient(MONGO_URI)

# define my db name
DB_NAME = ""

# read in the SESSION_KEY variable from the operating system environment
SESSION_KEY = os.environ.get('SESSION_KEY')

# set the session key
app.secret_key = SESSION_KEY





# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)