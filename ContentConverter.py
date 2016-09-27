import ImageMagick as IM
import os
import sys
import re
import imghdr
import math
import HandBrake as HB

#Python program to batch convert files from various multimedia formats to other multimedia formats.

#Syntax is:
#python ContentConverter.py inputFile

#Current flags:
#-h = help | display this help message
#-l filename = log output to given file | default = print output to console
#-i format = input format | default ='.tif' or '.tiff'
#-o format = output format |default = '.jpg'
#-s integer = max size | default = -1, or no rescaling
#-nr = no rescale | default = rescale to max size
#-v = video | Specifies file as a video file, for HandBrake
#-sw filename = log large files to given file | default = no logging


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
if("-h" in stuff):
	print "Usage: python ContentConverter.py [flags] inputDirectory"
	print ""
	print "-h = help | display this help message"
	print "-l filename = log output to given file | default = print output to console"
	print "-i format = input format | default ='.tif' or '.tiff'. If -v is on, default '.mpeg'"
	print "-o format = output format |default = '.jpg'. If -v, default ='.m4v'"
	print "-s integer = max size | default = -1, or no rescaling"
	print "-nr = no rescale | default = rescale to max size"
	print "-v = video | Specifies file as a video file, for HandBrake"
	print "-sw filename = log large files to given file | default = no logging"
	print "-standard = Archive standard | use standard settings based on format"
	sys.exit()
if("-standard" in stuff):
	stuff.remove("-standard")
	if("-v" in stuff):
		pass
	else:
		outextension='.jpg'
		max_size=100000
		rescale=True
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
	try:
		if(max_size==0):
			pass
	except: 
		max_size=-1
#Check the -nr flag
if("-nr" in stuff):
	stuff.remove("-nr")
	rescale=False
else:
	rescale=True
#Check the -v flag
if("-v" in stuff):
	stuff.remove("-v")
	if(extension==''):
		extension='.mpeg'
	if(outextension=='.jpg'):
		outextension='.m4v'
	video=True
else:
	video=False
#Check the -sw flag
if("-sw" in stuff):
	try:
		warningfile=open(stuff[stuff.index("-sw")+1],"w")
	except:
		print "File for size warnings not found"
	stuff.pop(stuff.index("-sw")+1)
	stuff.pop(stuff.index("-sw"))

else:
	warningfile=None
top=sys.argv[1]
print top
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
if(video):
	HB.convertVideo(top,examples,extension,outextension,max_size,logfile,warningfile)
else:
	print top,examples,extension,outextension,max_size,logfile,rescale
	IM.convertImage(top,examples,extension,outextension,max_size,logfile,rescale)
