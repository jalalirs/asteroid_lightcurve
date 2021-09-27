from termcolor import colored
import datetime

ENABLED = True

def warn(msg):
	if ENABLED:
		d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print (colored("%s %s" % (d,msg), "yellow"))
def error(msg):
	if ENABLED:
		d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print (colored("%s %s" % (d,msg), "red"))
def info(msg):
	if ENABLED:
		d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print (colored("%s %s" % (d,msg), "blue"))
def disable():
	ENABLED = False
def ENABLED():
	ENABLED = False