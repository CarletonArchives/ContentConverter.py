import re
import os
import sys
import math
def logOutput(output,logfile):
	if(logfile!=None):
		logfile.write(output+"\n")
	else:
		print output


#Convert each example
def convertImage(top,examples,extension,outextension,max_size,logfile,rescale):
	for example in examples:
	
		exit=False
		#Find the new filename, by replacing .tif or .tiff, or adding .jpg
		if(extension==''):
			tiff=re.compile("\.tiff?$")
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
					os.system("convert '"+example+"' -resize "+str(100*scale)+"% '"+ newstring+"'")
				except:
					logOutput("error dealing with file: "+example,logfile)
					exit=True
		logOutput(newstring+"\t"+str(os.path.getsize(newstring)),logfile)

