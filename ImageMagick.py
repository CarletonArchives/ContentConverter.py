import os
import sys
import re
import imghdr
import math

#Python program to run ImageMagick against all .tiffs in a directory, converting them to jpgs of <100k

#Syntax is:
#python ImageMagick.py inputFile


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
		
#Convert each example
for example in examples:

	exit=False
	#Find the new filename, by replacing .tif or .tiff, or adding .jpg
	if(extension==''):
		replace=tiff.search(example)
		if replace:
			newstring=example.replace(replace.group(),outextension)
		else:
			newstring=example+outextension

	else:
		newstring=example.replace(extension,outextension)
	if('/data/originals' in newstring):
		newstring=newstring.replace('/data/originals','/data/dips',1)
		newdirs=newstring.split('/')
		newpath=""
		for i in range(0,len(newdirs)-1):
			newpath+=newdirs[i]
			newpath+="/"
			try:
				os.chdir(newpath)
				os.chdir(top)
			except:
				os.mkdir(newpath)
	#Skip if the file is already converted
	try:
		if(max_size>0):
			if(os.path.getsize(newstring)<max_size):
				logOutput("File "+newstring+" already exists",logfile)
				exit=True
				continue
		else:
			os.path.getsize(newstring)
			logOutput("File "+newstring+" already exists",logfile)
	except:
		#If it isn't, try converting it
		try:
			os.system("convert '"+example.replace(" "," ")+"' '"+newstring.replace(" "," ")+"'")
		except:
			logOuput("Error converting file " +newstring,logfile)
			exit=True
	#If something clearly went wrong with it, skip this conversion	
	try: 
		os.path.getsize(newstring)
	except:
		logOutput("Error opening file " +newstring,logfile)
		exit=True
	#If you need to skip, leave	
	if(exit==True):
		continue

	if(max_size>0 and rescale):
		print os.path.getsize(newstring)>max_size
		scale=1
		#If the file isn't small enough, change the scale and reconvert until it fits.
		while(os.path.getsize(newstring)>max_size and exit==False):
			scale = scale*math.sqrt(max_size*1.0/os.path.getsize(newstring))
			logOutput("Scaling at "+str(math.sqrt(scale))+" times original",logfile)
			try:		
				os.system("convert "+example+" -resize "+str(100*scale)+"% "+ newstring)
			except:
				logOutput("error dealing with file: "+example,logfile)
				exit=True
	logOutput(newstring+"\t"+str(os.path.getsize(newstring)),logfile)
	
