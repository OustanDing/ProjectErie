import datetime, re, sqlite3
from flask import *
from tempfile import mkdtemp
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from datetime import timedelta, date, datetime
from operator import itemgetter

# FLASK SETUP
app = Flask(__name__)
app.secret_key = 'leonBong'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# DATABASE
conn = sqlite3.connect('data.db')
db = conn.cursor()

# TWILIO
account_sid = 'AC8343d4dd93fafa41efe6325eeeb5b2dd'
auth_token = '62280b30937320345c07b016e86a65c5'
client = Client(account_sid, auth_token)

if __name__ == '__main__':
	app.run(debug=True)