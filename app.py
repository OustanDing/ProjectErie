import datetime, re, sqlite3, requests
from flask import *
from tempfile import mkdtemp
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from datetime import timedelta, date, datetime
from operator import itemgetter
from math import sqrt
from threading import Timer

# FLASK SETUP
app = Flask(__name__)
app.secret_key = 'leonBong'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# DATABASE
conn = sqlite3.connect('data.db', check_same_thread=False)
db = conn.cursor()

# TWILIO
account_sid = 'AC8343d4dd93fafa41efe6325eeeb5b2dd'
auth_token = '62280b30937320345c07b016e86a65c5'
client = Client(account_sid, auth_token)

# GOOGLE MAPS
api_key = 'AIzaSyCOu4NPK-hWvyMx5bNCrOOvP2HXehwGCok'
# url = 

# CHECK INT FUNCTION
def checkInt(i):
	try:
		int(i)
		return True
	except ValueError:
		return False

# CALC DISTANCE BETWEEN 2 COORDINATE POINTS
def calc(p1, p2):
	p1split = p1.split(',')
	p2split = p2.split(',')
	x1 = float(p1split[0])
	y1 = float(p1split[1])
	x2 = float(p2split[0])
	y2 = float(p2split[1])

	xdist = (x2 - x1) * 111.32
	ydist = (y2 - y1) * 110.57

	dist = sqrt(xdist**2 + ydist**2)*1000

	return dist

reports = 0
score = 0

# SMS RESPONSE
@app.route('/sms', methods=['GET', 'POST'])
def sms():
	# Retrieve data in database
	data = []
	db.execute('SELECT * FROM points')
	temp = db.fetchall()

	for point in temp:
		data.append({
			'phone': point[0],
			'type': point[1],
			'severity': point[2].upper(),
			'location': point[3],
			'time': point[4]
			})

	# Retrieve users data
	users = {}
	db.execute('SELECT * FROM users')
	userstemp = db.fetchall()

	for user in userstemp:
		users[user[0]] = user[1]

	# Retrieve SMS info
	requested = request.form['Body']
	requestedlist = requested.split(' ')
	number = request.form['From']

	'''
	if requested.lower() == 'help':
		resp = MessagingResponse()
		resp.message('To report: report [type] [severity] [location]\n To query: query [location] [radius]')
		return str(resp)
	'''
	if requestedlist[0].lower() == 'report':
		if len(requestedlist) != 4:
			resp = MessagingResponse()
			resp.message('Invalid format. Proper: report [type] [severity] [location]')
			return str(resp)
		else:
			entry = {
				'type': requestedlist[1],
				'severity': requestedlist[2],
				'location': requestedlist[3]
			}

			global reports
			reports += 1

			global score
			if entry['severity'] == 'LOW':
				score += 8
			elif entry['severity'] == 'MID' or 'severity' == 'MEDIUM':
				score += 5
			elif entry['severity'] == 'HIGH':
				score += 2

			db.execute('INSERT INTO points VALUES (?, ?, ?, ?, ?)', (number, entry['type'], entry['severity'], entry['location'], datetime.now()))
			conn.commit()

			resp = MessagingResponse()
			resp.message('Added! {0} ({1} severity) at {2}'.format(entry['type'], entry['severity'], entry['location']))

			t = Timer(300.0, delete)
			t.start()

			return str(resp)

	elif requestedlist[0].lower() == 'query':
		if len(requestedlist) != 3:
			resp = MessagingResponse()
			resp.message('Invalid format. Proper: query [location] [radius]')
			return str(resp)
		elif not checkInt(requestedlist[2]):
			resp = MessagingResponse()
			resp.message('Search radius must be numeric.')
			return str(resp)
		else:
			sendMsg = ''
			req = {
				'location': requestedlist[1],
				'radius': float(requestedlist[2])
			}

			db.execute('SELECT * FROM points')
			points = db.fetchall()

			validpoints = []
			for point in points:
				print(calc(req['location'], point[3]))
				print(req['radius'])
				distance = calc(req['location'], point[3])
				if distance <= req['radius']:
					validpoints.append({
						'number': point[0],
						'type': point[1],
						'severity': point[2],
						'location': point[3],
						'dist': distance
						})

			for point in validpoints:
				sendMsg += (u'\n\u2022' + ' ' + str(point['dist']) + ' m away at ' + point['location'] + ': ' + point['type'].title() + ', ' + point['severity'] + ' severity. Pinged by ' + users[point['number']])

			if sendMsg == '':
				sendMsg = 'No matching queries.'

			'''
			resp = MessagingResponse()
			resp.message(sendMsg)

			return str(resp)

			'''
			message = client.messages.create(
				to = number,
				from_ = '+16475591371',
				body = sendMsg)
			

	else:
		resp = MessagingResponse()
		resp.message('Invalid command.')

		return str(resp)

	return redirect(url_for('/'))

@app.route('/delete')
def delete():
	db.execute('SELECT * FROM points')
	points = db.fetchall()
	for point in points:
		if datetime.now() - datetime.strptime(point[4], '%Y-%m-%d %H:%M:%S.%f') > timedelta(seconds=300):
			db.execute('DELETE FROM points WHERE time = ?', (point[4],))
			global reports
			reports -= 1
			global score
			if point[2] == 'LOW':
				score -= 8
			elif point[2] == 'MEDIUM' or point[2] == 'MID':
				score -= 5
			elif point[2] == 'HIGH':
				score -= 2
	conn.commit()

@app.route('/')
def index():
	# Retrieve users data
	users = {}
	db.execute('SELECT * FROM users')
	userstemp = db.fetchall()

	for user in userstemp:
		users[user[0]] = user[1]

	# Get data for map
	markers = []
	db.execute('SELECT * FROM points')
	pointdata = db.fetchall()
	for point in pointdata:
		markers.append({
			'coords': {'lat': point[3].split(',')[0], 'lng': point[3].split(',')[1]},
			'content': point[3] + ': ' + point[1].title() + ', ' + point[2] + ' severity. Pinged by ' + users[point[0]]})

	if reports != 0:
		score2 = score/reports
	else:
		score2 = '-'

	print(markers)
	return render_template('index.html', score = score2, markerdata = markers)

@app.route('/map')
def map():
	return render_template('map.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/howto')
def howto():
	return render_template('howto.html')

if __name__ == '__main__':
	app.run(debug=True)