#*****************************************************************************
#* Copyright 2017, Saudi Aramco.
#* All rights reserved.
#* Author:  jalalirs
#* Date:    12/17/2017
#* Project: Simulation Studio
#******************************************************************
import os, re
import sys
import subprocess
import getopt
import shlex
import time
import datetime, time, dateutil.parser as dateparser
import shutil
import errno
import fnmatch
import pickle
import random
import glob


"""
Implementing utility functions
"""

def cp(s,d):
	"""Copy single file from @s to @d"""
	shutil.copyfile(s,d)

def cpl(ss,ds):
	"""
	Copy multiple files from @ss to @ds
	Assert(@ss == @ds)
	"""
	for i in range(len(ss)):
		copy_file(ss[i],ds[i])

def mv(s,d):
	"""Move single file from @s to @d"""
	shutil.move(s,d)

def osc(command):
	"""Execute @command in os level and return the output"""
	p=subprocess.Popen(command, stdout=subprocess.PIPE,shell=True)
	out, err = p.communicate()
	return out

def osc2(command):
	"""Execute @command in os level and return the output and the error"""
	p=subprocess.Popen(command, stdout=subprocess.PIPE,shell=True)
	out, err = p.communicate()
	return out, err

def osc3(command):
    """Execute @command in os level and return the output and the error"""
    p=subprocess.Popen(command, stdout=subprocess.PIPE,shell=True)
    out, err = p.communicate()
    return out, err, p.returncode

def load_json(json_file_name):
	"""Load json file from @json_file_name"""
	import yaml
	try:
		f = open( json_file_name)
		string = f.read()
		# remove comments and tabs
		string = re.sub(re.compile("//.*?\n" ), "", string)
		string = string.replace("\t"," ")
		# load python object
		config = yaml.load(string)
		f.close()
	except Exception(e):
		print(e)
	return config

def chmod(f,m):
	"""Change single file @f permission with permission level @m"""
	os.chmod(f, m)

def rm(path):
	"""Delete a single file @path"""
	try:
		os.remove(path)
	except OSError as exception:
		if exception.errno != errno.ENOENT:
			raise

def is_file(path):
	"""Return True if the thing at @path is a file, False otherwise"""
	return os.path.isfile(path)

def exists(path):
	"""Return True if the thing at @path exists, False otherwise"""
	return os.path.exists(path)

def purge(dir, pattern):
	"""
	Remove all files and directories that satisfy @pattern 
	starting from @dir as a root
	"""
	for f in os.listdir(dir):
		if re.search(pattern,f):
			os.remove(os.path.join(dir,f))

def mkdir(path):
	"""Create a new directory at @path"""
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def rmdir(path):
	"""Delete a directory"""
	try:
		shutil.rmtree(path)
	except OSError as exception:
		if exception.errno != errno.ENOENT:
			raise

def open_file(filePath,mode="a"):
	"""
	Open a file at @filePath with mode @mode and
	return the file descriptor. 
	"""
	try:
		f = open(filePath, mode)
		return f
	except IOError:
		print ("Error: could not open",filePath)
		return None

def close_file(file):
	"""
	close the file with the file descriptor @file
	"""
	file.close()

def append_to_file(f,text):
	"""
	Append text @text to an opened for write file descriptor @f
	This function inserts a new line at the end of the appended text
	"""
	if text != "":
		f.write(text+"\n")

def read_file(file):
	"""Read a text file and return its content"""
	f=open_file(file,"r")
	if f == None:
	      return None
	fs= f.read()
	close_file(f)
	return fs

def ls(path, filesOnly=False, pattern=False):
	"""
	list file(s) in @path. 
	If @filesOnly is True, directories are omitted. 
	If @pattern is True, the function will treat the path as 
	a pattern and list all files and directories that satisfy it.
	"""
	if pattern:
		return glob.glob(path)
	if filesOnly:
		files = [ f for f in os.listdir(path) if is_file(os.path.join(path,f)) ]
	else:
		files = [ f for f in os.listdir(path)]
	return files

def match(regEx, text):
	"""
	Try to match the regular expression @regEx 
	in the text at @text. If match is found, all occurrences
	are returned, otherwise empty list is returned
	"""
	_regEx = re.compile(regEx)
	res = _regEx.search(text)
	if res:
		return list(res.groups())
	else:
		return []

def parent(path):
	"""return the parent path to @path"""
	return os.path.dirname(path)

def to_datetime(string,dformat):
	"""Create a datetime object from a @string given @format"""
	return datetime.datetime.strptime(string,dformat)


def load_json(json_file_name):
	config = None
	try:
		f = open(json_file_name)
		string = f.read()
		# remove comments and tabs
		string = re.sub(re.compile("//.*?\n" ), "", string)
		string = string.replace("\t"," ")
		# load python object
		config = json.loads(string)
		f.close()
	except Exception as e:
		print (e)
		raise
	return config

