import ImageMagick as IM
import os
import sys
import re
import imghdr
import math

#Python program to run ImageMagick against all .tiffs in a directory, converting them to jpgs of <100k

#Syntax is:
#python ImageMagick.py inputFile

#Current flags:
#-l filename = log output to given file | default = print output to console
#-i format = input format | default ='.tif' or '.tiff'
#-o format = output format |default = '.jpg'
#-s integer = max size | default = -1, or no rescaling
#-nr = no rescale | default = rescale to max size

#TODO: 
#Add format options, .pdf, .docx, video, audio (so it handles pdfs, etc.)
#Probably should include a list of common options for the Archives.

#Known Bugs:
#Will not convert anything with a ' in the filename.




def logOutput(output,logfile):
	if(logfile!=None):
		logfile.write(output+"\n")
	else:
		print output


examples=[]
stuff=sys.argv
#Check the -l flag
if("-l" in stuff):
	try:
		logfile=stuff[stuff.index("-l")+1]
		stuff.remove(logfile)
		stuff.remove("-l")
		logfile=open(logfile,"w")
	except:
		print "Error in logfile"
		logfile=None
else:
	logfile=None
#Check the -i flag
if("-i" in stuff):
	extension=stuff[stuff.index("-i")+1]
	stuff.pop(stuff.index("-i")+1)
	stuff.pop(stuff.index("-i"))
	print extension
else:
	extension=''
	tiff=re.compile("\.tiff?$")
#Check the -o flag
if("-o" in stuff):
	outextension=stuff[stuff.index("-o")+1]
	stuff.pop(stuff.index("-o")+1)
	stuff.pop(stuff.index("-o"))
	print outextension
else:
	outextension='.jpg'
#Check the -s flag
if("-s" in stuff):
	try:
		max_size=int(stuff[stuff.index("-s")+1])
	except:
		max_size=-1
	stuff.pop(stuff.index("-s")+1)
	stuff.pop(stuff.index("-s"))
	print max_size
else:
	max_size=-1
#Check the -nr flag
if("-nr" in stuff):
	stuff.remove("-nr")
	rescale=False
else:
	rescale=True
top=sys.argv[1]
#If they are bad at typing directories, don't bother doing anything.
try:
	os.chdir(top)
except:
	logOutput("Directory "+str(top)+" not found.",logfile)
	sys.exit()
#Otherwise, walk through directory tree, and add .tiffs to examples
for root,dirs,files in os.walk(top):
	for test in files:
		if(extension==''):
			try:
				temp=imghdr.what(root+"/"+test)
			except:
				temp=''
			if temp=='tiff':
				logOutput("Found "+root+"/"+test+" with correct type",logfile)
				examples.append(root+"/"+test)
		elif (test.endswith(extension) and (root+"/"+test).find('/data/meta')==-1):
			logOutput("Found "+root+"/"+test+" with correct type",logfile)
			examples.append(root+"/"+test)
IM.convertImage(top,examples,extension,outextension,max_size,logfile,rescale)
