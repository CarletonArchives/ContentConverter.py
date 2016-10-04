import ImageMagick as IM
import os
import sys
import re
import imghdr
import math
import HandBrake as HB
import ffmpeg as fmpg

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
#-a = audio | Specifies file as audio, for ffmpeg
#-sw filename = log large files to given file | default = no logging


#TODO: 
#Add format options, .pdf, .docx
#Change Video to ffmpeg
#Clean up -nr flag
#Figure out standard video and audio options
#Test, Test, Test
#More?

#Known Bugs:
#Will not convert anything with a ' in the filename.




def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output

global params
params={}
examples=[]
stuff=sys.argv
#Yes, I did write my own flag handler, and yes, I am a genuine idiot. But I don't care. This also allows me to set up defaults and stuff in the way I like.
#Look at the current calls for examples. Note that maxargs=-1 reads up to the next -flag structure in argv.
def grabFlag(args,flag,fields,defaults,maxargs):
	if(flag in args):
		values=[]
		i=args.index(flag)+1
		while((args[i][0]!="-") if i<len(args) else False):
			values.append(args[i])
			i+=1
		i-=1
		back=args.index(flag)
		while(i!=back-1):
			args.pop(i)
			i-=1
		if(maxargs>=0 and len(values)>maxargs):
			print flag + " flag has too many arguments! "+maxargs+" required, "+len(values)+" given"
			sys.exit()
		if len(fields)>len(values):
			i=0
			for value in values:
				params[fields[i]]=value
				i+=1
			while(i<len(fields)):
				if(defaults[i]!=None):
					params[fields[i]]=defaults[i]
				i+=1
		if len(fields)==len(values):
			i=0
			for value in values:
				params[fields[i]]=value
				i+=1
		if len(fields)<len(values):
			i=0
			for field in fields:
				params[field]=values[i]
				i+=1
			spot=i-1
			params[fields[spot]]=[params[fields[spot]]]
			while(i<len(values)):
				params[fields[spot]].append(values[i])
				i+=1
	return args
#The flags. First, check if it is audio, video, or picture
stuff=grabFlag(stuff,"-v",['type','extension','outextension'],['video','.mpeg','.m4v'],0) #Check -v flag
stuff=grabFlag(stuff,"-a",['type','extension','outextension'],['audio','.wav','.mp3'],0) #Check -a flag

if('type' not in params):
	stuff=grabFlag(stuff,"-standard",['max_size','outextension','rescale'],[100000,'.jpg',True],0) #Grab the -standard flag
elif (params['type']=='video'):
	stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile'],[100000000,'.m4v','toobig.out'],0) #For video
elif (params['type']=='audio'):
	stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile'],[10,'.mp3','toobig.out'],0) #And for audio

stuff=grabFlag(stuff,"-s",['max_size'],[None],1) #Grab the -s flag
stuff=grabFlag(stuff,"-i",['extension'],[None],1) #Grab the -i flag
stuff=grabFlag(stuff,"-o",['outextension'],[None],1) #Grab the -o flag
stuff=grabFlag(stuff,"-sw",['warningfile'],[None],1) #Grab the -sw flag
stuff=grabFlag(stuff,"-l",['logfile'],[None],1) #Grab the -l flag
stuff=grabFlag(stuff,"-ef",['errorfile'],[None],1) #Grab the -ef flag
stuff=grabFlag(stuff,"-args",['extra_args'],[None],1) #Grab extra args for ffmpeg??
if('extra_args' not in params):
	params['extra_args']=''
print stuff
#Display help message
if("-h" in stuff):
	help=open("help.txt","r")
	for i in help:
		print i,
	help.close()
	sys.exit()
#Check the -nr flag
if("-nr" in stuff):
	stuff.remove("-nr")
	rescale=False
else:
	rescale=True
	params['rescale']=True
top=sys.argv[1]
params['top']=top
print top
print params
if ('max_size' in params): #Make sure that the size is an integer
	try:
		params['max_size']=int(params['max_size'])
	except:
		print "Size given was not an int"
		sys.exit()
if ('warningfile' in params): #And that the oversize log file exists
	try:
		params['warningfile']=open(params['warningfile'],"w")
	except:
		print "Invalid file listed for size warnings"
		sys.exit()
if('logfile' in params): #And the normal log file too.
	try:
		params['logfile']=open(params['logfile'],"w")
	except:
		print "Invalid log file"
		sys.exit()
if('errorfile' in params): #And the file for errors.
	try:
		params['errorfile']=open(params['errorfile'],"w")
	except:
		print "Invalid error file"
		sys.exit()
#If they are bad at typing directories, don't bother doing anything.
try:
	os.chdir(top)
except:
	logOutput("Directory "+str(top)+" not found.",params)
	sys.exit()
#Otherwise, walk through directory tree, and add .tiffs to examples
#This section preserves some old functionality. For images, it was trained to look at the header using imghdr, in addition to the extension. Probably should be removed or changed to a flag.
for root,dirs,files in os.walk(top):
	for test in files:
		if('extension' not in params):
			try:
				temp=imghdr.what(root+"/"+test)
			except:
				temp=''
			if temp=='tiff':
				logOutput("Found "+root+"/"+test+" with correct type",params)
				examples.append(root+"/"+test)
		elif (test.endswith(params['extension']) and (root+"/"+test).find('/data/meta')==-1):
			logOutput("Found "+root+"/"+test+" with correct type",params)
			examples.append(root+"/"+test)
#Pick the conversion tool based on type.
if('type' in params):
	if('type'=='video'):
		HB.convertVideo(examples,params)
	else:
		fmpg.convertAudio(examples,params)
else:
	IM.convertImage(examples,params)
