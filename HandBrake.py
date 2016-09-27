import os
import sys

def logOutput(output,logfile):
	if(logfile!=None):
		logfile.write(output+"\n")
	else:
		print output

def convertVideo(top,examples,extension,outextension,max_size,logfile,warningfile):
	for example in examples:
	
		exit=False
		#Find the new filename, by replacing .tif or .tiff, or adding .jpg
		if(extension==''):
			extension='.mpeg'
		if example.find(extension)>0:
			newstring=example.replace(extension,outextension)
		else:
			newstring=example+outextension
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
				os.system("HandBrakeCLI -i '"+example+"' -o '"+newstring+"'")
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
	
		if(max_size>0 and warningfile!=None):
			#If the file isn't small enough, change the scale and reconvert until it fits.
			if(os.path.getsize(newstring)>max_size):
				logOutput("The file was big enough to generate a warning",logfile)
				warningfile.write(newstring+"\n")
		logOutput(newstring+"\t"+str(os.path.getsize(newstring)),logfile)

