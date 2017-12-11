import re
import os
import sys
import math
import PyPDF2 as pypdf2
import BatchConverter as conv

def isAlreadyCorrect(path,comparePath,params):
	if(not os.path.isfile(path)):
		return False
	if(path==comparePath): #Forces compression attempt
		return False
	if(not path.split(".")[-1] in params['outextension']):
		return False

	if('ifoversize' in params['force'] and 'max_size' in params):
		if(params['max_size']<os.path.getsize(path)):
			return False
	if(comparePath==None):
		return True
	if('ifbigger' in params['force']):
		if(not os.path.isfile(comparePath)):
			return False
		if(os.path.getsize(path)>os.path.getsize(comparePath)):
			return False
	return True

def compress(inPath,outPath,params):
	try:
		ret=os.system("gs -q -sstdout=%stderr -dNOPAUSE -dBATCH -sDEVICE=pdfwrite "+params['extra_args']+" -sOutputFile='"+outPath+"' '"+inPath+"' 2>/dev/null")
		if (ret!=0):
			conv.logOutput("Error converting file " + outPath,params)
			print "\n"+ "Error converting file " + outPath
			conv.logError(inPath,params)
			return False
	except:
		conv.logOutput("Error converting file " + outPath,params)
		print "\n"+ "Error converting file " + outPath
		conv.logError(inPath,params)
		return False
	return True

def copy(inPath,outPath,params):
	try:
		ret=os.system("cp '"+inPath+"' '"+outPath+"'")
		if(ret!=0):
			conv.logOutput("Error copying file " + outPath,params)
			print "\n"+ "Error copying file " + outPath
			conv.logError(inPath,params)
			return False
	except:
		conv.logOutput("Error copying file " + outPath,params)
		print "\n"+ "Error copying file " + outPath
		conv.logError(inPath,params)
		return False
	return True
