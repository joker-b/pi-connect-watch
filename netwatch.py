#! /bin/python

import os
import sys
import subprocess
import time
import platform

def connected(Target=None):
	target=Target 
	if Target is None:
		target = 'google.com'
	if 'Darwin' in platform.system():
		cmd = 'ping -c 2 -W 1 %s >&/dev/null'%(target)
	else:
		cmd = 'ping -c 2 -w 1 %s >&/dev/null'%(target)
	result = subprocess.call(cmd.split(),shell=False)
	return (result != 0)

def simple_loop(Delay=10,Target=None):
	while True:
		print connected(Target=Target)
		time.sleep(Delay)

def finite_loop(Delay=10,Count=4,Target=None):
	n = 0
	for i in range(0,Count):
		c = connected(Target=Target)
		print c
		if c is True:
			n += 1
		time.sleep(Delay)
	return n



if __name__ == '__main__':
	print 'test time'
	for trg in ['linkedin.com','liynksdasygdgs.org']:
		r = finite_loop(4,3,trg)
		print 'got %d of 4 success on %s' % (r,trg)
