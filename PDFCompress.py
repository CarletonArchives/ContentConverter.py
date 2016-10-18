import re
import os
import sys
import math
import PyPDF2 as pypdf2

def logOutput(output,params):
	if('logfile' in params):
		params['logfile'].write(output+"\n")
	else:
		print output
def logError(filename,params):
	if('errorfile' in params):
		params['errorfile'].write(filename+"\n")
#Convert each example
def compressPDF(examples,params):
	for example in examples:
	
		exit=False
		#Always converts from pdf to pdf
		params['extension']='.pdf'
		params['outextension']='.pdf'
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
		else:
			if('errorfile' in params and '/dips' not in newstring):
				logError(example,params)
				continue
			elif('/dips' not in newstring):
				newstring=newstring.replace('.pdf','___2.pdf')
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
				ret=os.system("gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite -dCompatibilityLevel=1.3 -dPDFSETTINGS=/screen "+params['extra_args']+" -sOutputFile='"+newstring+"' '"+example+"'")
				print ret
				if (ret!=0):
					logOutput("Error converting file " +newstring,params)
					logError(example,params)
					exit=True
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
	
		if('max_size' in params and 'warningfile' in params):
			#If the file isn't small enough, output to warning
			if(os.path.getsize(newstring)>params['max_size'] and exit==False):
				logOutput("The file was big enough to generate a warning",params)
				params['warningfile'].write(example+"\n")
		logOutput(newstring+"\t"+str(os.path.getsize(newstring)),params)

