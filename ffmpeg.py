import os
import sys
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
			print "\nOriginal was smaller\n"
			return False
	#If the bitrate is too high, it's wrong.
	if(params['type']=='video'):
		try:
			dur=subprocess.Popen("ffprobe -i '"+path+"' -show_entries format=duration -v quiet -of csv='p=0'",shell=True,stdout=subprocess.PIPE).stdout
			dur=float(dur.readline())
			dur2=subprocess.Popen("ffprobe -i '"+comparePath+"' -show_entries format=duration -v quiet -of csv='p=0'",shell=True,stdout=subprocess.PIPE).stdout
			dur2=float(dur2.readline())
			if(8*os.path.getsize(path)/dur/1000>8*os.path.getsize(comparePath)/dur2/1000):
				print "\nOriginal had lower bit rate\n"
				return False
		except:
			return False
	return True

def compress(inPath,outPath,params):
	try:
		ret=os.system("ffmpeg -y -loglevel panic -i '"+inPath+"' " +params['extra_args']+" '"+outPath+"' ")
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
	if(os.path.isfile(outPath)):
			ret = os.system("rm '"+outPath+"'")
			if(ret!=0):
				conv.logOutput("Error removing existing file " + outPath,params)
				print "\n"+ "Error removing existing file " + outPath
				conv.logError(outPath,params)
				return False
	if("."+outPath.split(".")[-1] != "."+inPath.split(".")[-1]):
		outPath=outPath.replace("."+outPath.split(".")[-1], "."+inPath.split(".")[-1])
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

