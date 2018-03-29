import re
import os
import sys
import math
import subprocess
import BatchConverter as conv

def isAlreadyCorrect(path,comparePath,params):
	#If it doesn't exist, it's wrong.
	if(not os.path.isfile(path)):
		path=path.replace("."+path.split(".")[-1], params['extension'])
		if(not os.path.isfile(path)):
			return False
	#If it doesn't have a valid extension, it's wrong.
	if(not "."+path.split(".")[-1] in params['outextension']):
		return False
	if(path==comparePath): #Forces compression attempt
		return False
	#If we care about output size and it's too big, it's wrong.
	if('ifoversize' in params['force'] and 'max_size' in params):
		if(params['max_size']<os.path.getsize(path)):
			return False
	#If there is no original to compare to, it's valid now.
	if(comparePath==None):
		return True
	#If the original is smaller, it's wrong.
	if('ifbigger' in params['force']):
		if(os.path.getsize(path)>os.path.getsize(comparePath)):
			return False
	return True

#Convert each example
def convert(inPath,outPath,params,*stats):
	try:
		ret=os.system("convert -quiet '"+inPath.replace("'","'\\''")+"' '"+outPath.replace("'","'\\''")+"'")
		if (ret!=0):
			conv.logOutput("Error converting file " + outPath,params)
			print "\n"+ "Error converting file " + outPath
			conv.logError(inPath,params)
			if(len(stats)>0):
				stats[0]['errors']+=1
				return False,stats[0]
			return False
		if(params['rescale']=='True' and 'max_size' in params):
			scale=((params['max_size'])*1.0)/(1.0*os.path.getsize(outPath))
			conv.logOutput("Rescaling at " + str(scale) + " times original",params)
			ret=os.system("convert -quiet '"+inPath.replace("'","'\\''")+"' -resize "+str(math.sqrt(10000*scale))+"% -define jpeg:extent="+str(params['max_size'])+" '"+outPath.replace("'","'\\''")+"'")
			if(ret!=0):
				conv.logOutput("Error converting file with scaling " + outPath,params)
				print "\n"+ "Error converting file with scaling" + outPath
				conv.logError(inPath,params)
				if(len(stats)>0):
					stats[0]['errors']+=1
					return False,stats[0]
				return False
	except:
		conv.logOutput("Error converting file, exception on " + outPath,params)
		print "\n"+ "Error converting file " + outPath
		conv.logError(inPath,params)
		if(len(stats)>0):
			stats[0]['errors']+=1
			return False,stats[0]
		return False
	if(len(stats)>0):
		stats[0]['conversions']+=1
		return True,stats[0]
	return True

def copy(inPath,outPath,params,*stats):
	if(os.path.isfile(outPath)):
			ret = os.system("rm '"+outPath+"'")
			if(ret!=0):
				conv.logOutput("Error removing existing file " + outPath,params)
				print "\n"+ "Error removing existing file " + outPath
				conv.logError(outPath,params)
				if(len(stats)>0):
					stats[0]['errors']+=1
					return False,stats[0]
				return False
	if("."+outPath.split(".")[-1] != "."+inPath.split(".")[-1]):
		outPath=outPath.replace("."+outPath.split(".")[-1], "."+inPath.split(".")[-1])
	try:
		ret=os.system("cp '"+inPath+"' '"+outPath+"'")
		if(ret!=0):
			conv.logOutput("Error copying file " + outPath,params)
			print "\n"+ "Error copying file " + outPath
			conv.logError(inPath,params)
			if(len(stats)>0):
				stats[0]['errors']+=1
				return False,stats[0]
			return False
	except:
		conv.logOutput("Error copying file " + outPath,params)
		print "\n"+ "Error copying file " + outPath
		conv.logError(inPath,params)
		if(len(stats)>0):
			stats[0]['errors']+=1
			return False,stats[0]
		return False
	if(len(stats)>0):
		stats[0]['copies']+=1
		return True,stats[0]
	return True
