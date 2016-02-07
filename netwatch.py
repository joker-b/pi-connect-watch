#! /bin/python

import os
import sys
import subprocess as sp
import time
import platform
import math
import random
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
		dnull = open('biglog.log','a')
	result = sp.call(cmd.split(),shell=False,stderr=sp.STDOUT,stdout=dnull)
	dnull.close()
	print "%s: result was %d for %s" % (time.asctime(),result,target)
	if result == 2:
		sv.rotate()
	return (result != 2)

def endless_logging(Delay=10,Variance=3,Target=None):
	global logName
	while True:
		t = time.time()
		c = connected(Target=Target)
		if not c:
			t = -t
		fp = open(logName,'a')
		fp.write('%d\n'%(t))
		fp.close()
		d = Delay
		if Variance != 0:
			d = d + random.randint(-Variance,Variance)
		time.sleep(d)

def read_log(LogFile=None,Start=None):
	global logName
	entries = []
	if LogFile is not None:
		if os.path.exists(LogFile):
			logName = LogFile
		else:
			print 'No file "%s" so using "%s"' % (LogFile,logName)
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
	report = 'Time span: %d hours, %d samples' % (thours,len(entries))
	nUp = len([e for e in entries if e['c']])
	report = report + '\n%d%% Uptime' % (100*nUp/len(entries))
	return report

def chart_js_uptime(entries):
	if len(entries) < 1:
		return '<p>No Entries.</p>'
	T0 = entries[0]['t']
	if len(entries) < 2:
		return 'Time %s: %s' % (time.ctime(T0), entries[0]['c'])
	TN = entries[len(entries)-1]['t']
	tspan = TN-T0
	thours = max(1,int(math.floor((tspan/3600.0))))
	nUp = len([e for e in entries if e['c']])
	html = """
<html><head>
	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Time', 'Status'],
 """
	html = html + ',\n'.join(['[%d,%d]'%(e['t'],((0+e['c']))) for e in entries])
	html = html + """]);
        var options = {
          title: 'Uptime over %d hours',
          hAxis: {title: 'Time'},
          vAxis: {title: 'Status', minValue: -0.25, maxValue: 0.25},
          legend: 'none'
        };
        var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
    </head><body>
""" % (thours)
	html = html + '<p>Time span: %d hours, %d samples</p>' % (thours,len(entries))
	html = html + '<p><b style="color: #FF3420">%d%% Uptime</b></p>' % (100*nUp/len(entries))	
	html = html + """
    <div>
    <h3>Chart:</h3>
    <div id="chart_div" style="width: 900px; height: 500px;"></div>
    <p>End of chart</p>
    </div>
</body>
</html>
"""
	return html

def chart_uptime(entries,NumRows=20,NumCols=56):
	if len(entries) < 1:
		return '<p>No Entries.</p>'
	T0 = entries[0]['t']
	if len(entries) < 2:
		return 'Time %s: %s' % (time.ctime(T0), entries[0]['c'])
	TN = entries[len(entries)-1]['t']
	tspan = TN-T0
	thours = max(1,int(math.floor((tspan/3600.0))))
	nUp = len([e for e in entries if e['c']])
	allPct = 100*nUp/len(entries)
	estPct = NumCols*nUp/len(entries)
	html = "<html><body>"
	html = html + '<p>Time span: %d hours, %d samples</p>' % (thours,len(entries))
	html = html + '<p><b style="color: #FF3420">%d%% Uptime</b></p>' % (allPct)	
	rowSpan = tspan/NumRows
	html = html + '<p><i>%s</i></p>'%(time.ctime(T0))
	html = html + '<p>'
	lowest = 100
	highest = 0
	mark = '*'
	tag = '=='
	bgc = 'white'
	fgc = '#9090e0'
	for i in range(0,NumRows):
		tStart = T0 + i*rowSpan
		tEnd = tStart + rowSpan
		sube = [e for e in entries if e['t']>=tStart and e['t']<=tEnd]
		if len(sube) > 0:
			nUp = len([e for e in sube if e['c']])
			fpct = 100 * nUp / len(sube)
			pct = NumCols * nUp / len(sube)
			mark = '*'
			bgc = '#e09090'
		else:
			fpct = allPct
			pct = estPct
			mark = '?'
			bgc = '#e0b0b0'
		lowest = min(lowest,fpct)
		highest = max(highest,fpct)
		html = html + '<span style="background-color: %s;">' %(fgc)
		html = html + ('&nbsp;' * pct) + mark + '</span>'
		if (pct < NumCols):
			html = html + '<span style="background-color: %s;">' %(bgc)
			html = html + ('&nbsp;' * (NumCols-pct))
			html = html + '</span>'
		html = html + ' % 3d%% <i>(%d)</i><br/>' % (fpct,len(sube))
	html = html + "</p>"
	html = html + '<p><i>%s</i></p>'%(time.ctime(TN))
	html = html + "<p><i>Range of slices: %d%% to %d%%</i></p>" % (lowest,highest)
	html = html + "</body></html>"
	return html

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

def send_report(Subject='Connectivity Report',Body=None,Html=None):
	bodyText = Body
	if bodyText is None:
		bodyText = 'Report made at %s' % (time.ctime())
	htmlText = Html
	if htmlText is None:
		htmlText = '<html><body><p>%s</p></body></html>'%(bodyText)
	msg = MIMEMultipart('mixed')
	msg['From'] = 'Pi not 3 <kevin.bjorke@gmail.com>'
	msg['To'] = 'Kevin Bjorke <kevin.bjorke@gmail.com>'
	msg['Subject'] = Subject
	msg.preamble = 'weird why would you see this?'
	alt = MIMEMultipart('alternative')
	mbody = MIMEText(bodyText,'plain')
	mhtml = MIMEText(htmlText,'html')
	alt.attach(mbody)
	alt.attach(mhtml)
	msg.attach(alt)
	s = smtplib.SMTP('localhost')
	s.sendmail('kevin.bjorke@gmail.com', 'kevin.bjorke@gmail.com', msg.as_string())
	s.quit()

def old_test():
	ct=2
	for trg in ['linkedin.com','liynksdasygdgs.org',None]:
		print "checking again '%s'..." % (trg)
		r = finite_loop(Delay=3,Count=ct,Target=trg)
		print 'got %d of %d success on %s' % (r,ct,trg)

#############

if len(sys.argv)>1:
	entries = read_log(LogFile=sys.argv[1])
	print report_uptime(entries)
	#print chart_uptime(entries)
	st = time.asctime()
	send_report(Body=report_uptime(entries),Html=chart_uptime(entries),Subject='Testing %s'%(st))
	# send_report(Body=report_uptime(entries),Subject='Testing 2')
	exit()

if __name__ == '__main__':
	# old_test()
	t = time.time()
	print 'starting log at %d' % (t)
	endless_logging(Delay=3*60,Variance=120) # seven minutes

# eof
