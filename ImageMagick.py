import re
import os
import sys
import math
import subprocess
def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output
def logError(filename,params):
	if('errorfile' in params):
		params['errorfile'].write(filename+"\n")
#Convert each example
def convertImage(examples,params):
	for example in examples:
	
		exit=False
		#Find the new filename, by replacing .tif or .tiff, or adding .jpg
		if('extension' not in params):
			tiff=re.compile("\.tiff?$")
			replace=tiff.search(example)
			if replace:
				newstring=example.replace(replace.group(),params['outextension'])
			else:
				newstring=example+params['outextension']
	
		else:
			newstring=example.replace(params['extension'],params['outextension'])
		if('/originals' in newstring):
			newstring=newstring.replace('/originals','/dips',1)
			newdirs=newstring.split('/')
			newpath=""
			for i in range(0,len(newdirs)-1):
				newpath+=newdirs[i]
				newpath+="/"
				try:
					os.chdir(newpath)
					os.chdir(params['top'])
				except:
					os.mkdir(newpath)
		elif (params['extension']==params['outextension'] and '/dips' not in newstring):
			newstring=newstring.replace(params['outextension'],"___2"+params['outextension'])
		#Skip if the file is already converted
		try:
			if('max_size' in params):
				if(os.path.getsize(newstring)<params['max_size']):
					logOutput("File "+newstring+" already exists",params)
					exit=True
					continue
			else:
				os.path.getsize(newstring)
				logOutput("File "+newstring+" already exists",params)
		except:
			#If it isn't, try converting it
			try:
				command="convert '"+example.replace("'","'\\''")+"' '"+newstring.replace("'","'\\''")+"'"
				os.system(command)
			except:
				logOutput("Error converting file " +newstring,params)
				logError(example,params)
				exit=True
		#If something clearly went wrong with it, skip this conversion	
		try: 
			os.path.getsize(newstring)
		except:
			logOutput("Error opening file " +newstring,params)
			logError(example,params)
			exit=True
		#If you need to skip, leave	
		if(exit==True):
			continue
	
		if('max_size' in params and 'rescale' in params):
			scale=1
			#If the file isn't small enough, change the scale and reconvert until it fits.
			while(os.path.getsize(newstring)>params['max_size'] and exit==False):
				scale = scale*math.sqrt(params['max_size']*1.0/os.path.getsize(newstring))
				logOutput("Scaling at "+str(math.sqrt(scale))+" times original",params)
				try:	
					command = "convert '"+example.replace("'","'\\''")+"' -resize "+str(100*scale)+"% '"+newstring.replace("'","'\\''")+"'"
					os.system(command)
				except:
					logOutput("error dealing with file: "+example,params)
					logError(example,params)
					exit=True
				if(params['rescale']!=True):
					exit=True
		logOutput(newstring+"\t"+str(os.path.getsize(newstring)),params)

