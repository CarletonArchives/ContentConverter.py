import ImageMagick as IM
import os
import sys
import re
import imghdr
import math
import ffmpeg as fmpg
import PDFCompress as pdf

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
def doFileOperation(inPath,outPath,checkFunc,compressFunc,copyFunc,params,stats):
	if('force' not in params):
		params['force']='ifbigger'
	#If we should always compress, do it.
	if('always' in params['force']):
		return compressFunc(inPath,outPath,params,stats)
	#If there is a valid output, skip
	if(checkFunc(outPath,inPath,params)):
		logOutput("File "+outPath+" already is valid, skipping",params)
		stats['skipped']+=1
		return False,stats
	#If the input is a valid output, copy.
	if(checkFunc(inPath,inPath,params)): #If we can just copy the original file
		logOutput("File "+outPath+" is copied from original",params)
		return copyFunc(inPath,outPath,params,stats)
	#Try a compression
	if(not compressFunc(inPath,outPath,params)):
		stats['errors']+=1
		return False,stats
	#If the input is better than the output, copy
	if((not checkFunc(outPath,inPath,params)) and checkFunc(inPath,None,params)):
		logOutput("File "+outPath+" is copied from original",params)
		return copyFunc(inPath,outPath,params,stats)
	#If the end result is good, exit
	if(checkFunc(outPath,None,params)):
		stats['conversions']+=1
		#logOutput(outPath+"\t"+str(os.path.getsize(outPath)),params)
		return True,stats
	#Else error.
	logOutput("Error in output " +outPath,params)
	print "\n"+ "Error in file " +outPath
	logError(outPath,params)
	stats['errors']+=1
	return False,stats

stuff=sys.argv
def convertBatch(stuff,stats,formats):
	params={}
	examples=[]
	params=stuff
	top=params['top']
	params['extension']=params['input']
	params['outextension']=params['output']
	if('max_size' in params):
		params['max_size']=int(params['max_size'])
	if('extra_args' not in params):
		params['extra_args']=''
	if(os.path.isfile(params['top'])):
		params['usefile']=params['top']
		params['top']="/"
	if('usefile' in params): #Grab the relevant file names before there's any chance of modifying them
		top="/"
		params['top']="/"
		try:
			FileFile=open(params['usefile'],"rb")
		except:
			print "Can't open file list"
			sys.exit()
		lines=[]
		for line in FileFile:
			lines.append(line[:-1])
		FileFile.close()
	#If they are bad at typing directories, don't bother doing anything.
	try:
		os.chdir(top)
	except:
		logOutput("Directory "+str(top)+" not found.",params)
		sys.exit()
	#Otherwise, walk through directory tree, and add .tiffs to examples
	#This section preserves some old functionality. For images, it was trained to look at the header using imghdr, in addition to the extension. Probably should be removed or changed to a flag.
	if('usefile'not in params):
		for root,dirs,files in os.walk(top):
			for test in files:
				if(test[:2]!="._"):
					if(test.endswith(params['extension']) and (root+"/"+test).find('/data/meta')==-1):
						if('strict' in params):
							if(params['strict'].lower()=='true' and '/dips' in root+"/"+test):
								continue
						#logOutput("Found "+root+"/"+test+" with correct type",params)
						examples.append(root+"/"+test)
					elif("."+test.split(".")[-1] not in formats and (root+"/"+test).find('/data/meta')==-1):
						formats.append("."+test.split(".")[-1])
	else:
		for line in lines:
			if(os.path.isfile(line)):
				if(line.endswith(params['extension']) and line.find('/data/meta')==-1):
					if(params['strict'].lower()=='true' and '/dips' in line):
						continue
					#logOutput("Found "+line+" with correct type",params)
					examples.append(line)
				elif("."+line.split(".")[-1] not in formats and line.find('/data/meta')==-1):
					formats.append("."+line.split(".")[-1])
			else:
				logOutput("Error: couldn't find file "+line,params)
				logError(line,params)
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
			if('extension' not in params):
				params['extension']='.tiff'
			if('outextension' not in params):
				params['outextension']='.jpg'
			checkFunc=IM.isAlreadyCorrect
			compressFunc=IM.convert
			copyFunc=IM.copy
		#	stats=IM.convertImage(examples,params,stats)
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
			test,stats=doFileOperation(example,newstring,checkFunc,compressFunc,copyFunc,params,stats)
			if(not test):
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
	#else:
	#	stats=IM.convertImage(examples,params,stats)
	logOutput("Stats after "+params['input']+": "+str(stats),params)
	return stats,formats

if("BatchConverter.py"in sys.argv[0]):
	stats={'conversions':0,'skipped':0,'copies':0,'errors':0}
	convertBatch(sys.argv)
