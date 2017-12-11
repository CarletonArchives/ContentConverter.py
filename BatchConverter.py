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
	
	
def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output

def logError(filename,params):
	if('errorfile' in params):
		params['errorfile'].write(filename+"\n")
	else:
		print("\nError with file "+filename)

def makeNewFilePath(inPath,params):
	outPath=inPath.replace(params['extension'],params['outextension'].split(";")[0])
	if('/originals' in outPath):
		outPath=outPath.replace('/originals','/dips',1)
		dirsToAdd=outPath.split('/')
		testPath=""
		for i in range(0,len(dirsToAdd)-1):
			testPath+=dirsToAdd[i]
			testPath+="/"
			try:
				os.chdir(testPath)
				os.chdir(params['top'])
			except:
				os.mkdir(testPath)
	else:
		if('strict' in params and '/dips' not in outPath):
			if(params['strict']==True):
				logError(inPath,params)
				return False
		elif (params['extension']==params['outextension'] and '/dips' not in outPath):
			outPath=outPath.replace(params['outextension'],'___2'+params['outextension'])
	return outPath

#Converts or copies the file according to params['force']. Returns False if no change was made.
def doFileOperation(inPath,outPath,checkFunc,compressFunc,copyFunc,params):
	if('force' not in params):
		params['force']='ifbigger'
	#If we should always compress, do it.
	if('always' in params['force']):
		return compressFunc(inPath,outPath,params)
	#If there is a valid output, skip
	if(checkFunc(outPath,inPath,params)):
		logOutput("File "+outPath+" already is valid, skipping",params)
		return False
	#If the input is a valid output, copy.
	if(checkFunc(inPath,inPath,params)): #If we can just copy the original file
		logOutput("File "+outPath+" is copied from original",params)
		return copyFunc(inPath,outPath,params)
	#Try a compression
	if(not compressFunc(inPath,outPath,params)):
		return False
	#If the input is better than the output, copy
	if((not checkFunc(outPath,inPath,params)) and checkFunc(inPath,None,params)):
		logOutput("File "+outPath+" is copied from original",params)
		return copyFunc(inPath,outPath,params)
	#If the end result is good, exit
	if(checkFunc(outPath,None,params)):
		return True
	#Else error.
	logOutput("Error in output " +outPath,params)
	print "\n"+ "Error in file " +outPath
	logError(outPath,params)
	return False

stuff=sys.argv
def convertBatch(stuff):
	params={}
	examples=[]
	if('python' in stuff):
		#The flags. First, check if it is audio, video, or picture
		stuff=grabFlag(stuff,"-v",['type','extension','outextension'],['video','.mpeg','.m4v'],0) #Check -v flag
		stuff=grabFlag(stuff,"-a",['type','extension','outextension'],['audio','.wav','.mp3'],0) #Check -a flag
		stuff=grabFlag(stuff,"-p",['type','extension','outextension'],['pdf','.pdf','.pdf'],0) #Check -p flag
		if('type' not in params):
			stuff=grabFlag(stuff,"-standard",['max_size','outextension','rescale','errorfile'],[200000,'.jpg',False,'errors.txt'],0) #Grab the -standard flag
		elif (params['type']=='pdf'):
			stuff=grabFlag(stuff,"-standard",['max_size','warningfile','errorfile','extra_args'],[20000000,'toobig.out','errors.txt',"-dColorImageDownsampleType=/Bicubic -dColorImageResolution=60 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=60 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=60"],0) #For Pdfs
		elif (params['type']=='video'):
			stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile','extra_args','errorfile'],[100000000,'.m4v','toobig.out',' -strict -2 -crf 37.5','errors.txt'],0) #For video
		elif (params['type']=='audio'):
			stuff=grabFlag(stuff,"-standard",['max_size','outextension','warningfile','errorfile'],[100000000,'.mp3','toobig.out','errors.txt'],0) #And for audio
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
		if ('max_size' in params): #Make sure that the size is an integer
			try:
				params['max_size']=int(params['max_size'])
			except:
				print "Size given was not an int"
				sys.exit()
	else:
		params=stuff
		top=params['top']
		params['extension']=params['input']
		params['outextension']=params['output']
		if('max_size' in params):
			params['max_size']=int(params['max_size'])
		if('extra_args' not in params):
			params['extra_args']=''
	if('usefile' in params): #Grab the relevant file names before there's any chance of modifying them
		top="/"
		try:
			FileFile=open(params['usefile'],"rb")
		except:
			print "Can't open file list"
			sys.exit()
		lines=[]
		for line in FileFile:
			lines.append(line[:-1])
		FileFile.close()

	if('logfile' in params): #And the normal log file too.
		if(not isinstance(params['logfile'],file)):
			try:
				params['logfile']=open(params['logfile'],"w")
			except:
				params.pop('logfile')
				print "Invalid log file"
	if('errorfile' in params): #And the file for errors.
		if(not isinstance(params['errorfile'],file)):
			try:
				params['errorfile']=open(params['errorfile'],"wb")
			except:
				print "Invalid error file"
				sys.exit()
	if ('warningfile' in params): #Make sure that the oversize log file exists
		if(not isinstance(params['warningfile'],file)):
			try:
				params['warningfile']=open(params['warningfile'],"w")
			except:
				print "Invalid file listed for oversize warnings"
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
						if('strict' in params):
							if(params['strict'].lower()=='true' and '/dips' in root+"/"+test):
								continue
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
	if('force' in params):
		params['force']=params['force'].lower()
		if(params['force']=='both'):
			params['force']+='ifbiggerifoversize'
	if('max_size' in params):
		params['max_size']=int(params['max_size'])
	#Pick the conversion tool based on type.
	if('type' in params):
		if(params['type']=='video' or params['type']=='audio'):
			if('extension' not in params):
				params['extension']='.wav'
			checkFunc=fmpg.isAlreadyCorrect
			compressFunc=fmpg.compress
			copyFunc=fmpg.copy

		elif(params['type']=='pdf'):
			#pdf.compressPDF(examples,params)
			if('extension' not in params):
				params['extension']='.pdf'
			if('outextension' not in params):
				params['outextension']='.pdf'
			checkFunc=pdf.isAlreadyCorrect
			compressFunc=pdf.compress
			copyFunc=pdf.copy
		elif(params['type']=='image'):
			IM.convertImage(examples,params)
		if(params['type']!='image'):
			count=0
			for example in examples:
				count+=1
				sys.stdout.write("\rProcessing file "+str(count)+" of "+str(len(examples)))
				sys.stdout.flush()
				if(not os.path.isfile(example)):
					logOutput("File to convert does not exist " +example,params)
					print "\n"+ "File to convert does not exist " +example
					logError(example,params)
					continue

				#Find the new filename
				newstring=makeNewFilePath(example,params)
				if(not newstring):
					continue

				#Convert/Copy file, depending on params
				if(not doFileOperation(example,newstring,checkFunc,compressFunc,copyFunc,params)):
					continue

				#Note if the file is too big at the end.
				if('max_size' in params and 'warningfile' in params):
					#If the file isn't small enough, post a warning.
					if(not os.path.isfile(newstring)):
						newstring=newstring.replace("."+newstring.split(".")[-1], "."+example.split(".")[-1])
					if(os.path.getsize(newstring)>params['max_size']):
						logOutput("The file was big enough to generate a warning",params)
						params['warningfile'].write(example)
				logOutput(newstring+"\t"+str(os.path.getsize(newstring)),params)
	else:
		IM.convertImage(examples,params)
	if 'logfile' in params:
		params['logfile'].close()
	if 'errorfile' in params:
		params['errorfile'].close()
	if 'warningfile' in params:
		params['warningfile'].close()
if("BatchConverter.py"in sys.argv[0]):
	convertBatch(sys.argv)
