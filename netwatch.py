#! /bin/python

import os
import sys
import subprocess as sp
import time
import platform

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

# ######################

def connected(Target=None):
	target=Target 
	if Target is None:
		target = sv.server()
	if 'Darwin' in platform.system():
		cmd = 'ping -c 2 -W 1 %s'%(target)
	else:
		cmd = 'ping -c 2 -w 1 %s'%(target)
	dnull = open('/dev/null','w')
	result = sp.call(cmd.split(),shell=False,stderr=sp.STDOUT,stdout=dnull)
	dnull.close()
	if result != 0:
		sv.rotate()
	return result

def simple_loop(Delay=10,Target=None):
	while True:
		print connected(Target=Target)
		time.sleep(Delay)

def finite_loop(Delay=10,Count=4,Target=None):
	n = 0
	for i in range(0,Count):
		c = connected(Target=Target)
		if c == 0:
			n += 1
		if i < (Count-1):
			time.sleep(Delay)
	return n



if __name__ == '__main__':
	print 'test time'
	ct=4
	for trg in ['linkedin.com','liynksdasygdgs.org',None]:
		print "checking again '%s'..." % (trg)
		r = finite_loop(Delay=3,Count=ct,Target=trg)
		print 'got %d of %d success on %s' % (r,ct,trg)
