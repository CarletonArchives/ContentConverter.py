import ImageMagick as IM
import os
import sys
import re
import imghdr
import math
import ffmpeg as fmpg
import PDFCompress as pdf
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
	#-p = pdf | Specifies file as pdf, for ghostscript
	#-sw filename = log large files to given file | default = no logging
	#-ef filename = log errors to given file | default = no logging
	#-standard = use archive standard web compression settings
	#-args = extra args | grab extra args for ffmpeg, ghostscript
	
	
	#TODO: 
	#Add format options: .docx, .xls
	#Clean up -nr flag
	#Read in files to convert from data file?
	#Stop compressing small files?
	#More? Esp. w/ ImageMagick
	#Maybe some verbosity?
	#Test, Test, Test
	
	#Known Bugs:
	#Will not convert anything with a ' in the filename on non-images. Also, tons of problems with -f
	
	
	
	
def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output
params={}
examples=[]
stuff=sys.argv
def convertBatch(stuff):
	#Yes, I did write my own flag handler, and yes, I am a genuine idiot. But I don't care. This also allows me to set up defaults and stuff in the way I like.
	#Look at the current calls for examples. Note that maxargs=-1 reads up to the next -flag structure in argv.
	def grabFlag(args,flag,fields,defaults,maxargs):
		if(flag in args):
			values=[]
			i=args.index(flag)+1
			while(((args[i][0]!="-") if i<len(args) else False) and (i-args.index(flag)<=maxargs)):
				values.append(args[i])
				i+=1
			i-=1
			if(i-args.index(flag)>maxargs):
				print flag + " flag has too many arguments "+str(maxargs)+" required, "+str(len(values))+" given"
				sys.exit()
			back=args.index(flag)
			while(i!=back-1):
				args.pop(i)
				i-=1
			if(maxargs>0 and len(values)>maxargs):
				print flag + " flag has too many arguments! "+str(maxargs)+" required, "+str(len(values))+" given"
				sys.exit()
			if len(fields)>len(values):
				i=0
				if(maxargs!=0):
					for value in values:
						params[fields[i]]=value
						i+=1
				while(i<len(fields)):
					if(defaults[i]!=None):
						params[fields[i]]=defaults[i]
					i+=1
			elif len(fields)==len(values):
				i=0
				for value in values:
					params[fields[i]]=value
					i+=1
			elif len(fields)<len(values):
				i=0
				for field in fields:
					params[field]=values[i]
					i+=1
				spot=i-1
				params[fields[spot]]=[params[fields[spot]]]
				while(i<len(values)):
					params[fields[spot]].append(values[i])
					i+=1
			else:
				print "Something is very messed up.\n"
				sys.exit() 
		return args
	#The flags. First, check if it is audio, video, or picture
	stuff=grabFlag(stuff,"-v",['type','extension','outextension'],['video','.mpeg','.m4v'],0) #Check -v flag
	stuff=grabFlag(stuff,"-a",['type','extension','outextension'],['audio','.wav','.mp3'],0) #Check -a flag
	stuff=grabFlag(stuff,"-p",['type','extension','outextension'],['pdf','.pdf','.pdf'],0) #Check -p flag
	if('type' not in params):
		stuff=grabFlag(stuff,"-standard",['max_size','outextension','rescale','errorfile'],[100000,'.jpg',False,'errors.txt'],0) #Grab the -standard flag
	elif (params['type']=='pdf'):
		stuff=grabFlag(stuff,"-standard",['max_size','warningfile','errorfile','extra_args'],[20000000,'toobig.out','errors.txt',"-dColorImageDownsampleType=/Bicubic -dColorImageResolution=60 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=60 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=60"],0) #For Pdfs
	elif (params['type']=='video'):
		stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile','extra_args','errorfile'],[100000000,'.m4v','toobig.out',' -strict -2 -crf 37.5 -loglevel panic','errors.txt'],0) #For video
	elif (params['type']=='audio'):
		stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile','errorfile'],[100000000,'.mp3','toobig.out','errors.txt'],0) #And for audio
	print stuff
	stuff=grabFlag(stuff,"-s",['max_size'],[None],1) #Grab the -s flag
	stuff=grabFlag(stuff,"-i",['extension'],[None],1) #Grab the -i flag
	stuff=grabFlag(stuff,"-o",['outextension'],[None],1) #Grab the -o flag
	stuff=grabFlag(stuff,"-sw",['warningfile'],[None],1) #Grab the -sw flag
	stuff=grabFlag(stuff,"-l",['logfile'],[None],1) #Grab the -l flag
	stuff=grabFlag(stuff,"-ef",['errorfile'],[None],1) #Grab the -ef flag
	stuff=grabFlag(stuff,"-args",['extra_args'],[None],1) #Grab extra args for ffmpeg??
	stuff=grabFlag(stuff,"-f",['usefile'],['in.txt'],0)
	if('extra_args' not in params):
		params['extra_args']=''
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
		params['rescale']=False
	elif('rescale' not in params):
		rescale=True
		params['rescale']=True
	if('usefile' not in params):
		top=sys.argv[1]
	else:
	
		params['usefile']=sys.argv[1]
		top="/"
	params['top']=top
	print top
	print params
	if('usefile' in params): #Grab the relevant file names before there's any chance of modifying them
		try:
			FileFile=open(params['usefile'],"rb")
		except:
			print "Can't open file list"
			sys.exit()
		lines=[]
		for line in FileFile:
			lines.append(line[:-1])
		FileFile.close()
	if ('max_size' in params): #Make sure that the size is an integer
		try:
			params['max_size']=int(params['max_size'])
		except:
			print "Size given was not an int"
			sys.exit()
	if('logfile' in params): #And the normal log file too.
		try:
			params['logfile']=open(params['logfile'],"w")
		except:
			print "Invalid log file"
			sys.exit()
	if('errorfile' in params): #And the file for errors.
		try:
			params['errorfile']=open(params['errorfile'],"wb")
		except:
			print "Invalid error file"
			sys.exit()
	if ('warningfile' in params): #Make sure that the oversize log file exists
		try:
			params['warningfile']=open(params['warningfile'],"w")
		except:
			print "Invalid file listed for size warnings"
			sys.exit()
	
	#If they are bad at typing directories, don't bother doing anything.
	try:
		os.chdir(top)
	except:
		logOutput("Directory "+str(top)+" not found. Did you exceed the max arguments for a flag?",params)
		sys.exit()
	#Otherwise, walk through directory tree, and add .tiffs to examples
	#This section preserves some old functionality. For images, it was trained to look at the header using imghdr, in addition to the extension. Probably should be removed or changed to a flag.
	if('usefile'not in params):
		for root,dirs,files in os.walk(top):
			for test in files:
				if(test[:2]!="._"):
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
	else:
	
		for line in lines:
			try:
				if('extension' not in params):
					try:
						temp=imghdr.what(line)
					except:
						temp=''
					if temp=='tiff':
						logOutput("Found "+line+" with correct type",params)
						examples.append(line)
				elif (line.endswith(params['extension']) and line.find('/data/meta')==-1):
					logOutput("Found "+line+" with correct type",params)
					examples.append(line)
			except:
				logOutput("Did not find file "+line+" with correct type!\n",params)
	#Pick the conversion tool based on type.
	if('type' in params):
		if(params['type']=='video'):
			fmpg.convertAudio(examples,params)
		elif(params['type']=='pdf'):
			pdf.compressPDF(examples,params)
		elif(params['type']=='audio'):
			fmpg.convertAudio(examples,params)
	else:
		IM.convertImage(examples,params)
	if 'logfile' in params:
		params['logfile'].close()
	if 'errorfile' in params:
		params['errorfile'].close()
	if 'warningfile' in params:
		params['warningfile'].close()
