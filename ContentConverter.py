import sys
import os
import BatchConverter
import re
import shlex
import ConfigParser

top=os.path.abspath(sys.argv[1])
config=ConfigParser.RawConfigParser()
if(os.path.split(sys.argv[0])[0]!=""):
	os.chdir(os.path.split(sys.argv[0])[0])
here=os.getcwd()
config.read('contentConverterConfig.cfg')
formats={}

newformats=[]
run=[]
#BatchConverter.convertBatch(sys.argv)
for root,dirs,files in os.walk(top):
	extension=re.compile("\..{0,4}$")
	for filename in files:
		match= re.search(extension,filename)
		if(match!=None):
			if(not config.has_option('Formats',match.group(0).lower())):
				if(match.group(0).lower() not in newformats):
					newformats.append(match.group(0).lower())
			else:
				filetype=match.group(0).lower()
				if(filetype in formats):
					continue
				formats[filetype]=config.get('Formats',filetype)
				params={}
				if(config.has_section(formats[filetype]+'Defaults')):
					params['type']=(formats[filetype].lower())
					for item, val in config.items(formats[filetype]+'Defaults'):
							params[item]=val
				else:
					print "Error: Could not find config section "+formats[filetype]+'Defaults'
					continue
				if(config.has_section(filetype)):
					for item, val in config.items(filetype):
						params[item]=val
				params['input']=filetype
				params['top']=top
				run.append(params)
for thing in run:
	try:
		print "Starting conversion of format: "+thing['input']+" using arguments:"
		print thing
		BatchConverter.convertBatch(thing)
		print "\rProcessed files"
		print "Conversion finished, cleaning up"
		os.system("cat log.txt >> "+here+"/fullLog.txt")
		os.system("rm log.txt")
		os.system("cat errors.txt >> "+here+"/fullErrors.txt")
		os.system("rm errors.txt")
		os.system("cat toobig.out >> "+here+"/tooBig.txt")
		os.system("rm toobig.out")
		print "...............................\n"
	except:
		print "Error with format: "+thing['input']
out="Unused formats: "
for word in newformats:
	out+= word +" ; "
print out
