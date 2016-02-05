#! /bin/python

import os
import sys
import subprocess as sp
import time
import platform
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SV:
	TC=0
	servers = ['google.com','linkedin.com','yahoo.com']
	def server(self):
		return self.servers[self.TC]
	def rotate(self):
		"try another server target, in case of server failure"
		self.TC = self.TC + 1
		if self.TC >= len(self.servers):
			self.TC = 0

global sv
sv = SV()
global logName
logName = '%s_uptime.log' % (platform.uname()[1])

# ######################

def connected(Target=None):
	target=Target 
	if Target is None:
		target = sv.server()
	if 'Darwin' in platform.system():
		cmd = 'ping -c 2 -W 1 %s'%(target)
	elif 'Windows' in platform.uname():
		cmd = 'ping -n 2 -w 1 %s'%(target)
	else:
		cmd = 'ping -c 2 -w 1 %s'%(target)
	if 'Windows' in platform.uname():
		dnull = open('junk.txt','w')
	else:
		dnull = open('/dev/null','w')
	result = sp.call(cmd.split(),shell=False,stderr=sp.STDOUT,stdout=dnull)
	dnull.close()
	if result != 0:
		sv.rotate()
	return result

def endless_logging(Delay=10,Target=None):
	fp = open(logName,'a')
	while True:
		t = time.time()
		c = connected(Target=Target)
		if c != 0:
			t = -t
		fp.write('%d\n'%(t))
		time.sleep(Delay)

def read_log(Start=None):
	entries = []
	if not os.path.exists(logName):
		print 'log unavailable'
		return entries
	now = time.time()
	if Start is None:
		logStart = now - (3600*24*7)   # one week back
	else:
		logStart = Start
	fp = open(logName,'r')
	while True:
		fl = fp.readline()
		if fl == "":
			break
		fv = float(fl)
		up = (fv >= 0.0)
		fv = abs(fv)
		if fv >= logStart:
			entries.append({'t':fv, 'c': up})
	fp.close()
	return entries

def report_uptime(entries):
	if len(entries) < 1:
		return "No log entries"
	T0 = entries[0]['t']
	if len(entries) < 2:
		return 'Time %s: %s' % (time.ctime(T0), entries[0]['c'])
	TN = entries[len(entries)-1]['t']
	tspan = TN-T0
	thours = max(1,int(math.floor((tspan/3600.0))))
	return 'Time span: %d hours' % (thours)

#######

def finite_loop(Delay=10,Count=4,Target=None):
	n = 0
	for i in range(0,Count):
		c = connected(Target=Target)
		if c == 0:
			n += 1
		if i < (Count-1):
			time.sleep(Delay)
	return n

def send_report(Subject='Connectivity Report',Body=None):
	bodyText = Body
	if bodyText is None:
		bodyText = 'Report made at %s' % (time.ctime())
	Html = '<p>%s</p>'%(bodyText)
	msg = MIMEMultipart('mixed')
	msg['From'] = 'P not 3 <kevin.bjorke@gmail.com>' # fix this
	msg['To'] = 'Kevin Bjorke <kevin.bjorke@gmail.com>'
	msg['Subject'] = Subject
	msg.preamble = 'weird why would you see this?'
	alt = MIMEMultipart('alternative')
	mtxt = MIMEText(bodyText)
	mhtml = MIMEText(Html)
	alt.attach(mtxt)
	alt.attach(mhtml)
	msg.attach(alt)
	s = smtplib.SMTP('localhost')
	s.sendmail('kevin.bjorke@gmail.com', 'kevin.bjorke@gmail.com', msg.as_String())
	s.quit()

def old_test():
	ct=4
	for trg in ['linkedin.com','liynksdasygdgs.org',None]:
		print "checking again '%s'..." % (trg)
		r = finite_loop(Delay=3,Count=ct,Target=trg)
		print 'got %d of %d success on %s' % (r,ct,trg)

#############

if len(sys.argv)>1:
	entries = read_log()
	print report_uptime(entries)
	exit()

if __name__ == '__main__':
	t = time.time()
	print 'starting log at %d' % (t)
	endless_logging(Delay=7*60) # seven minutes

# eof
