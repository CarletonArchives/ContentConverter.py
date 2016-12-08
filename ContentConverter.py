import sys
import os
import BatchConverter
import re
import shlex
here=os.getcwd()
hi=sys.argv[1]
print here
print hi
formats=dict({'.png':"ContentConverter.py "+hi+" -l log.txt -i .png -o .jpg -standard",
'.jpg':"ContentConverter.py "+hi+" -l log.txt -i .jpg -o .jpg -standard", 
'.tif':"ContentConverter.py "+hi+" -l log.txt -i .tif -o .jpg -standard", 
'.pdf':"ContentConverter.py "+hi+" -l log.txt -i .pdf -p -standard",
'.tiff':"ContentConverter.py "+hi+" -l log.txt -i .tiff -o .jpg -standard", 
'.m4v':"ContentConverter.py "+hi+" -l log.txt -i .m4v -v -standard",
'.wav':"ContentConverter.py "+hi+" -l log.txt -i .wav -v -standard", 
'.mp4':"ContentConverter.py "+hi+" -l log.txt -i .mp4 -v -standard", 
'.mp3':"ContentConverter.py "+hi+" -l log.txt -i .mp3 -a -standard",
'.mpeg':"ContentConverter.py "+hi+" -l log.txt -i .mpeg -v -standard", 
'.ogg':"ContentConverter.py "+hi+" -l log.txt -i .ogg -v -standard", 
'.avi':"ContentConverter.py "+hi+" -l log.txt -i .avi -v -standard",
".jpeg":"ContentConverter.py "+hi+" -l log.txt -i .jpeg -o .jpg -standard"
})
newformats=[]
run=dict({})
#BatchConverter.convertBatch(sys.argv)
for root,dirs,files in os.walk(hi):
	extension=re.compile("\..{0,4}$")
	for filename in files:
		match= re.search(extension,filename)
		if(match!=None):
			if(match.group(0).lower() not in formats):
				if(match.group(0).lower() not in newformats):
					newformats.append(match.group(0).lower())
			else:
				run.update(dict([[match.group(0).lower(),formats[match.group(0).lower()]]]))
for key in run.keys():
	try:
		print "Starting conversion of format: "+key+" using arguments:"
		print run[key]
		BatchConverter.convertBatch(shlex.split(run[key]))
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
		print "Error with format: "+key
out="Unused formats: "
for word in newformats:
	out+= word +" ; "
print out
