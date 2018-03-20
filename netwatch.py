#! /bin/python

import os
import sys
import subprocess as sp
import time
import platform
import math
import random
import inspect
import getpass
import smtplib
import urllib2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PingService:
  TC=0
  servers = ['google.com','linkedin.com','yahoo.com']
  def server(self):
    return self.servers[self.TC]
  def rotate(self):
    "try another server target, in case of server failure"
    self.TC = self.TC + 1
    if self.TC >= len(self.servers):
      self.TC = 0

# #################

class IPWatch:
  v4 = "?"
  v6 = "?"
  prev4 = None
  prev6 = None
  def __init__(self,DeviceName,LogName="current_ip.log"):
    self.deviceName = DeviceName
    self.logName = LogName
    self.update()
    self.notify('Startup')
    self.log()
  def notify(self,Reason):
    "send email because IP addresses have changed (or at startup)"
    bodyText = 'IPv4: {}\nIPv6 {}\n'.format(self.v4,self.v6)
    htmlText = '<html><body><ul>\n'
    htmlText += '<li><b>IPv4</b> {}</li>\n'.format(self.v4)
    htmlText += '<li><b>IPv6</b> {}</li>\n'.format(self.v6)
    htmlText += '</ul></body></html>'
    msg = MIMEMultipart('mixed')
    msg['From'] = '{} <kevin.bjorke@gmail.com>'.format(self.deviceName)
    msg['To'] = 'Kevin Bjorke <kevin.bjorke@gmail.com>'
    msg['Subject'] = "{} {} IP Report".format(self.deviceName,Reason)
    msg.preamble = 'odd why would you see this?'
    alt = MIMEMultipart('alternative')
    mbody = MIMEText(bodyText,'plain')
    mhtml = MIMEText(htmlText,'html')
    alt.attach(mbody)
    alt.attach(mhtml)
    msg.attach(alt)
    try:
      s = smtplib.SMTP('localhost')
      s.sendmail('kevin.bjorke@gmail.com', 'kevin.bjorke@gmail.com', msg.as_string())
      s.quit()
    except:
      print "Sendmail Connection Error on IP Change"
      return False
    return True

  def log(self):
    "no check for file system failure"
    with open(self.logName,"w") as fp:
      fp.write('{}\n{}\n'.format(self.v4,self.v6))
  def check_for_change(self):
    "Get the current IP address. If it has changed, send a notification"
    self.update()
    with open(self.logName,"r") as fp:
      n4 = fp.readline().strip()
      n6 = fp.readline().strip()
      matched = self.v4 == n4 and self.v6 == n6
      if not matched:
        print('"IP address appears to have changed from "{}" to "{}"'.format(n4, self.v4))
        self.notify('Change')
        self.log()
  def get(self):
    return (self.v4, self.v6)
  def update(self):
    try:
      response = urllib2.urlopen('http://ipv4.icanhazip.com')
      self.v4 = response.read().strip()
      response = urllib2.urlopen('http://ipv6.icanhazip.com')
      self.v6 = response.read().strip()
    except:
      self.v4 = '??'
      self.v6 = '??' 

# #################

class NetWatch:
  machine = platform.uname()[1]
  pingService = PingService()
  firstReportDelay = 600 # ten minutes, in seconds
  reportInterval = 3600*24*7 # seven days, in seconds
  def __init__(self):
    self.userName = getpass.getuser()
    self.initEmailNames()
    self.initScriptPath()
    self.logFileName = os.path.join(self.scriptPath,'%s_uptime.log' % (self.machine))
    self.reportTimer = 0
    self.notifyFirstTime = True
    self.initialReportComplete = False
    self.ipw = IPWatch(self.names[self.machine])

  def initEmailNames(self):
    self.names = {}
    self.names[self.machine] = 'R Pi' # may be overwritten in the list below
    self.names['pinot3'] = 'Pi Not 3'
    self.names['arc'] = 'Arc Pi',
    self.names['blinky'] = 'Blinky Pi'
    self.names['rad'] = 'Rad Pi'
    self.names['new3'] = 'The New 3'
    self.names['less0'] = 'Less Zero'
    self.names['more0'] = 'More Zero'

  def initScriptPath(self):
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    dir = os.path.dirname(os.path.abspath(filename))
    print "Data in '%s'" % (dir)
    self.scriptPath = dir

  # ######################

  def connected(self,Target=None):
    target=Target 
    if Target is None:
      target = self.pingService.server()
    if 'Darwin' in platform.system():
      cmd = 'ping -c 2 -W 1 %s'%(target)
    elif 'Windows' in platform.uname():
      cmd = 'ping -n 2 -w 1 %s'%(target)
    else:
      cmd = 'ping -c 2 -w 1 %s'%(target)
    try:
      if 'Windows' in platform.uname():
        dnull = open('junk.txt','w')
      else:
        dnull = open('/dev/null','w')
      result = sp.call(cmd.split(),shell=False,stderr=sp.STDOUT,stdout=dnull)
      dnull.close()
    except:
      print "null open failure"
      return False
    print "%s: result was %d for %s" % (time.asctime(),result,target)
    if result == 2:
      self.pingService.rotate()
      if self.notifyFirstTime:
        print "You may need to use sudo to run this program"
    self.notifyFirstTime = False
    return (result != 2)

  def endless_logging(self,Delay=10,Variance=3,Target=None):
    while True:
      now = time.time()
      if not self.connected(Target=Target):
        now = -now
      else:
        self.ipw.check_for_change()
      try:
        fp = open(self.logFileName,'a')
        fp.write('%d\n'%(now))
        fp.close()
      except:
        print "Unable to write to logfile '%s' at time %d" % (self.logFileName, now)
        return # not so endless
      print "logged at %d (%d, %d)" % (self.reportTimer, self.firstReportDelay, self.reportInterval)
      sleepTime = Delay
      if Variance != 0:
        sleepTime = sleepTime + random.randint(-Variance,Variance)
      time.sleep(sleepTime)
      self.reportTimer = self.reportTimer+sleepTime
      if self.reportTimer >= self.firstReportDelay and not self.initialReportComplete:
        if self.create_all_reports("Startup"):
          print "initial report sent"
          self.initialReportComplete = True
        else:
          print "initial report failed?"
        if self.reportTimer >= self.reportInterval:
          if self.create_all_reports():
            self.reportTimer = 0

  def read_log(self,LogFile=None,Start=None):
    entries = []
    if LogFile is not None:
      if os.path.exists(LogFile):
        self.logFileName = LogFile
      else:
        print 'Reading log "%s"' % (self.logFileName)
    if not os.path.exists(self.logFileName):
      print 'log unavailable for reading'
      return entries
    now = time.time()
    if Start is None:
      logStart = now - self.reportInterval
    else:
      logStart = Start
    try:
      fp = open(self.logFileName,'r')
    except:
      print "Cannot open log '%s'" % (self.logFileName)
      return entries
    while True:
      fl = fp.readline()
      if fl == "":
        break
      try:
        fv = float(fl)
        up = (fv >= 0.0)
        fv = abs(fv)
        if fv >= logStart:
          entries.append({'t':fv, 'c': up})
      except:
        print "Bad number value '%s' ignored" % (fl)
    fp.close()
    return entries

  def report_uptime(self,entries):
    if len(entries) < 1:
      return "No log entries for designated interval"
    T0 = entries[0]['t']
    if len(entries) < 2:
      return 'Time %s: %s' % (time.ctime(T0), entries[0]['c'])
    TN = entries[len(entries)-1]['t']
    tspan = TN-T0
    thours = max(1,int(math.floor((tspan/3600.0))))
    report = 'Time span: %d hours, %d samples' % (thours,len(entries))
    nUp = len([e for e in entries if e['c']])
    report = report + ', %d%% Uptime' % (100*nUp/len(entries))
    return report

  def chart_js_uptime(self,entries):
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

  def chart_uptime(self,entries,NumRows=30,NumCols=40):
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
    rowSpan = tspan/NumRows
    html = html + '<p><i>Start: %s</i><br/>\n'%(time.ctime(T0))
    lowest = 100
    highest = 0
    mark = '*'
    tag = '=='
    bgc = 'white'
    fgc = '#b0e0b0'
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
        mark = '*'
        bgc = '#e0c0b0'
      lowest = min(lowest,fpct)
      highest = max(highest,fpct)
      html = html + '<span style="background-color: %s;">' %(fgc)
      html = html + ('&nbsp;' * pct) + mark + '</span>'
      if (pct < NumCols):
        html = html + '<span style="background-color: %s;">' %(bgc)
        html = html + ('&nbsp;' * (NumCols-pct))
        html = html + '</span>'
      html = html + ' % 3d%%<br/>\n' % (fpct)
    html = html + '<i>End: %s</i></p>\n'%(time.ctime(TN))
    html = html + "<p><i>Connectivity Range: %d%% to %d%%</i><br/>\n" % (lowest,highest)
    html = html + 'across %d hours (%d samples)</p>\n' % (thours,len(entries))
    html = html + '<p><b style="color: #FF3420">%d%% Overall Uptime</b></p>\n' % (allPct)  
    html = html + "</body></html>"
    return html

  #######

  def finite_loop(self,Delay=10,Count=4,Target=None):
    n = 0
    for i in range(0,Count):
      c = self.connected(Target=Target)
      if c == 0:
        n += 1
      if i < (Count-1):
        time.sleep(Delay)
        self.reportTimer = self.reportTimer+Delay
    return n

  def send_report(self,Subject='Generic Report',Body=None,Html=None):
    bodyText = Body
    if bodyText is None:
      bodyText = 'Report made at %s' % (time.ctime())
    self.ipw.update()
    bodyText += '\nIPv4: {}\nIPv6 {}\n'.format(self.ipw.v4,self.ipw.v6)
    htmlText = Html
    if htmlText is None:
      htmlText = '<html><body><p>%s</p></body></html>'%(bodyText)
    htmlText += '\n<ul><li>IPv4: {}</li><li>IPv6 {}</li></ul>\n'.format(self.ipw.v4,self.ipw.v6)
    msg = MIMEMultipart('mixed')
    msg['From'] = '%s %s <kevin.bjorke@gmail.com>' % (self.names[self.machine],self.userName)
    msg['To'] = 'Kevin Bjorke <kevin.bjorke@gmail.com>'
    msg['Subject'] = Subject
    msg.preamble = 'weird why would you see this?'
    alt = MIMEMultipart('alternative')
    mbody = MIMEText(bodyText,'plain')
    mhtml = MIMEText(htmlText,'html')
    alt.attach(mbody)
    alt.attach(mhtml)
    msg.attach(alt)
    try:
      s = smtplib.SMTP('localhost')
      s.sendmail('kevin.bjorke@gmail.com', 'kevin.bjorke@gmail.com', msg.as_string())
      s.quit()
    except:
      print "Sendmail Connection Error"
      return False
    return True

  def old_test(self):
    ct=2
    for trg in ['linkedin.com','liynksdasygdgs.org',None]:
      print "checking again '%s'..." % (trg)
      r = self.finite_loop(Delay=3,Count=ct,Target=trg)
      print 'got %d of %d success on %s' % (r,ct,trg)

  def create_all_reports(self,LogFile=None):
    reportName = LogFile
    if reportName is None or os.path.exists(reportName):
        reportName = "Standard"
    entries = self.read_log(LogFile)
    print self.report_uptime(entries)
    st = time.asctime()
    bt = self.report_uptime(entries)
    ht = self.chart_uptime(entries)
    return self.send_report(Body=bt,Html=ht,Subject='Connectivity Report: %s %s %s'%(reportName,self.machine,st))

#############

watcher = NetWatch()

if len(sys.argv)>1:
  watcher.create_all_reports(sys.argv[1])
  exit()

if __name__ == '__main__':
  # watcher.old_test()
  t = time.time()
  print 'starting log at %d' % (t)
  watcher.endless_logging(Delay=3*60,Variance=120) # seven minutes

# eof
