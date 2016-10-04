import os
import sys

def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output
def logError(filename,params):
	if('errorfile' in params):
		params['errorfile'].write(filename+"\n")
#This loop has way too many breaks within it for error handling. But it works, and does not miss anything, which is more important than size of code.
def convertAudio(examples,params):
	for example in examples:
	
		exit=False
		#Find the new filename, by replacing .tif or .tiff, or adding .jpg
		if('extension' not in params):
			params['extension']='.wav'
		if example.find(params['extension'])>0:
			newstring=example.replace(params['extension'],params['outextension'])
		else:
			newstring=example+params['outextension']
		#Check for bag structure, if so, place in dips.
		if('/data/originals' in newstring):
			newstring=newstring.replace('/data/originals','/data/dips',1)
			newdirs=newstring.split('/')
			newpath=""
			#This logic mirrors directories in originals into dips.
			for i in range(0,len(newdirs)-1):
				newpath+=newdirs[i]
				newpath+="/"
				try:
					os.chdir(newpath)
					os.chdir(params['top'])
				except:
					os.mkdir(newpath)
		#Skip if the file is already converted to the required specs.
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
				os.system("ffmpeg -i '"+example+"'" +params['extra_args']+" '"+newstring+"' ")
			except:
				logOuput("Error converting file " +newstring,params)
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
	
		if('max_size' in params and 'warningfile' in params):
			#If the file isn't small enough, post a warning.
			if(os.path.getsize(newstring)>params['max_size']):
				logOutput("The file was big enough to generate a warning",params)
				params['warningfile'].write(newstring+"\n")
		logOutput(newstring+"\t"+str(os.path.getsize(newstring)),params)

