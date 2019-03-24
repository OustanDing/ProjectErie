import sqlite3, random
from math import *
from datetime import datetime

# DATABASE
conn = sqlite3.connect('data.db', check_same_thread=False)
db = conn.cursor()

points = []
types = ['trash', 'algae']
sev = ['LOW', 'MID', 'HIGH']

for i in range(100):
	'''points.append({
		'phone': '+16472780505',
		'type': types[random.random(0, 1).round()],
		'severity': sev[random.random(0, 2).round()]
		'location': str(random.random(41.95, 42.10)) + ',' str(random.random(81.24, 81.4))
		})'''
	db.execute('INSERT INTO points VALUES (?, ?, ?, ?, ?)', ('+16472780505', types[random.randrange(0, 1, 1)], sev[random.randrange(0, 2, 1)], str(random.uniform(41.5, 42.5)) + ',' + str(random.uniform(-79, -83)), datetime.now()))

conn.commit()