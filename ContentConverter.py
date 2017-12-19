import sys
import os
import BatchConverter
import re
import shlex
import copy
import ConfigParser
from Tkinter import *
from tkFileDialog import *
import tkFileDialog, Tkinter
top={}
if(len(sys.argv)>1):
	top['top']=os.path.abspath(sys.argv[1])
config=ConfigParser.RawConfigParser()
if(os.path.split(sys.argv[0])[0]!=""):
	os.chdir(os.path.split(sys.argv[0])[0])
here=os.getcwd()
if(not 'top' in top):
	top['top']=here

config.read('contentConverterConfig.cfg')
formats=[]

execute={}

Window=Tkinter.Tk()
temp=StringVar()
temp.set(top['top'])
top['top']=temp
def get_default_config(config):
	params={}
	params2={}
	if(config.has_section('Defaults')):
		for item,val in config.items('Defaults'):
			string=StringVar()
			string.set(val)
			params[item]=string
			params2[item]=val
	return params,params2

def propagate_option_change(filetype):
	for item in execute:
		if((execute[item][3]==filetype or filetype=="Default") and execute[item][1].cget("relief")!=Tkinter.SUNKEN):
			for var in originals[filetype]:
				if(var in run[item]):
					if(isinstance(run[filetype][var],StringVar) and isinstance(run[item][var],StringVar)):
						run[item][var].set(originals[filetype][var])
						originals[item][var]=originals[filetype][var]

def make_button_changer(filetype):
	def change_button():
		if(filetype=="Default"):
			for thing in execute:
				execute[thing][2].set(execute[filetype][2].get())
		else:
			for thing in execute:
				if(execute[thing][3]==filetype):
					execute[thing][2].set(execute[filetype][2].get())
	return change_button

def setup_format_input(parent, formats):
	Boxes=[Tkinter.Label(parent,text="Formats  "),Tkinter.Label(parent,text="Filetype Options")]
	Boxes[0].grid(column=0,row=0,sticky=Tkinter.NW,pady=0)
	Boxes[1].grid(column=1,row=0,sticky=Tkinter.N,pady=0)
	Boxes={}
	i=1
	for box in formats:
		on=IntVar()
		on.set(1)
		if(box[0]!=box[1]):
			Boxes[box[0]]=[Tkinter.Checkbutton(parent,text=box[0],anchor=Tkinter.W,indicatoron=0,bd=2,width=5,selectcolor='#0f0'),Tkinter.Button(parent, text = "Options", command = createFiletypeButtonFunc(parent.winfo_toplevel(),box[0]), pady=0),on,box[1]]
			Boxes[box[0]][0].config(variable=Boxes[box[0]][2])
			Boxes[box[0]][0].grid(column=0,row=i,sticky=Tkinter.NW,pady=0)
			Boxes[box[0]][1].grid(column=1,row=i,sticky=Tkinter.N,pady=0)
		elif(box[0]=="Default"):
			Boxes[box[0]]=[Tkinter.Checkbutton(parent,text="All",command=make_button_changer("Default"),anchor=Tkinter.W,indicatoron=0,bd=2,width=5,selectcolor='#0f0'),Tkinter.Button(parent, text = "Options", command = createFiletypeButtonFunc(parent.winfo_toplevel(),box[0]), pady=0),on,box[1]]
			Boxes[box[0]][0].config(variable=Boxes[box[0]][2])
			Boxes[box[0]][0].grid(column=0,row=i,sticky=Tkinter.NW,pady=0)
			Boxes[box[0]][1].grid(column=1,row=i,sticky=Tkinter.N,pady=0)
		else:
			Boxes[box[0]]=[Tkinter.Checkbutton(parent,text=box[0],command=make_button_changer(box[0]),anchor=Tkinter.W,indicatoron=0,bd=2,width=5,selectcolor='#0f0'),Tkinter.Button(parent, text = "Options", command = createFiletypeButtonFunc(parent.winfo_toplevel(),box[0]), pady=0),on,box[1]]
			Boxes[box[0]][0].config(variable=Boxes[box[0]][2])
			Boxes[box[0]][0].grid(column=0,row=i,sticky=Tkinter.NW,pady=0)
			Boxes[box[0]][1].grid(column=1,row=i,sticky=Tkinter.N,pady=0)
		i+=1
	return Boxes

def ParamCurry(params,string,param,parent): #Returns a 0 argument file chooser function for buttons
	def getDir():
		temp=string.get()
		string.set(tkFileDialog.asksaveasfilename(initialdir=here,initialfile=string.get().split("/")[-1],parent=parent,title= "Choose the directory for the "+param))
		if(string.get()!=""):
			temp=string.get()
		string.set(temp)
	return getDir

def create_option_editor(parent, *filetype):
	OptionsBox=Tkinter.Frame(parent)
	string="Default"
	extensionoptions=[]
	if(len(filetype)>1):
		string=filetype[1]
		ExtensionBox=Tkinter.Frame(OptionsBox,borderwidth=2,padx=0,relief=Tkinter.GROOVE)
		if(config.has_section(filetype[1])):
			extensionoptions=config.options(filetype[1])
			setup_format_options(ExtensionBox,string,config.options(filetype))
		ExtensionBox.grid(column=0,row=3,sticky=Tkinter.NW)

	filetypeoptions=[]
	if(len(filetype)>0):
		if(len(filetype)==1):
			string=filetype[0]
		FileTypeBox=Tkinter.Frame(OptionsBox,borderwidth=2,padx=0,relief=Tkinter.GROOVE)
		if(config.has_section(filetype[0]+"Defaults")):
			filetypeoptions=config.options(filetype[0]+"Defaults")
			for option in filetypeoptions:
				if(option in extensionoptions):
					filetypeoptions.remove(option)
			setup_format_options(FileTypeBox,string,filetypeoptions)
		FileTypeBox.grid(column=0,row=2,sticky=Tkinter.NW)

	DefaultBox=Tkinter.Frame(OptionsBox,borderwidth=2,padx=0,relief=Tkinter.GROOVE)
	
	defaultoptions=config.options("Defaults")
	for option in defaultoptions:
		if(option in filetypeoptions or option in extensionoptions):
			defaultoptions.remove(option)
	setup_format_options(DefaultBox,string,defaultoptions)
	DefaultBox.grid(column=0,row=1,sticky=Tkinter.NW)

	FiletypeLabel=Tkinter.Label(OptionsBox,pady=0,text=string+" Settings")
	FiletypeLabel.grid(column=0,row=0,sticky=Tkinter.N)

	ButtonBox=Tkinter.Frame(OptionsBox)
	Buttons=[]
	Buttons.append(Tkinter.Button(ButtonBox,text="Defaults",command=reset_to_defaults(string)))
	Buttons.append(Tkinter.Button(ButtonBox,text="Reset",command=make_option_reseter(string)))
	Buttons.append(Tkinter.Button(ButtonBox,text="Save",command=make_option_saver(string)))

	for button in Buttons:
		button.grid(row=0,column=Buttons.index(button)+2,sticky=Tkinter.E)
	ButtonBox.grid(column=0,row=4,sticky=Tkinter.S)

	OptionsBox.grid(column=1,row=0,sticky=Tkinter.N)

def make_option_saver(filetype):
	def save_options():
		for var in run[filetype].keys():
			if(isinstance(run[filetype][var],StringVar)):
				originals[filetype][var]=run[filetype][var].get()
		if(filetype in execute):
			execute[filetype][1].config(relief=Tkinter.SUNKEN)
		propagate_option_change(filetype)
	return save_options
	
def make_option_reseter(filetype):
	def reset_options():
		for var in run[filetype].keys():
			if(isinstance(run[filetype][var],StringVar)):
				run[filetype][var].set(originals[filetype][var])
	return reset_options

def reset_to_defaults(filetype):
	def default_options():
		temp={}
		temp2={}
		temp,temp2=get_all_format_defaults(config,temp,temp2)
		originals[filetype]=temp2[filetype]
		make_option_reseter(filetype)()
		if(filetype in execute):
			execute[filetype][1].config(relief=Tkinter.RAISED)
		propagate_option_change(filetype)
	return default_options

def createFiletypeButtonFunc(parent,filetype):
	def buttonFunc():
		replace=parent.grid_slaves(column=1,row=0)
		fileToReset=parent.grid_slaves(column=1,row=0)
		if(len(fileToReset)>0):
			fileToReset=fileToReset[0].grid_slaves(column=0,row=0)
			if(len(fileToReset)>0):
				fileToReset=fileToReset[0].cget("text")
				fileToReset=fileToReset[:-9]
				make_option_reseter(fileToReset)()
		for widget in replace:
			widget.destroy()
		if(filetype=="Default"):
			create_option_editor(parent)
		elif(config.has_section(filetype+"Defaults")):
			create_option_editor(parent,filetype)
		else:
			create_option_editor(parent, config.get("Formats",filetype),filetype)
	return buttonFunc

def setup_format_options(parent,filetype,options):
	Boxes=[]
	for param in options:
		if('file' in param):
			Boxes.append([Tkinter.Label(parent,text=param+": "),Tkinter.Button(parent,anchor=Tkinter.W,pady=0,padx=0,textvariable=run[filetype][param], bg='white',width=30,borderwidth=2,relief=Tkinter.SUNKEN,command = ParamCurry(run[filetype],run[filetype][param],param,parent))])
		elif(run[filetype][param].get()=='True' or run[filetype][param].get()=='False'):
			Boxes.append([Tkinter.Label(parent,text=param+": "),Tkinter.Checkbutton(parent,onvalue='True',offvalue='False',variable=run[filetype][param],anchor=Tkinter.W,bd=2,width=5)])
		else:
			Boxes.append([Tkinter.Label(parent,text=param+": "),Tkinter.Entry(parent,textvariable=run[filetype][param],bd=2,width=30)])
	for Box in Boxes:
		Box[0].grid(column=0,row=Boxes.index(Box),sticky=Tkinter.NE)
		Box[1].grid(column=1,row=Boxes.index(Box),sticky=Tkinter.NW)

def GetFilenameCurry(current,parent): #Returns a 0 argument file chooser function for buttons
	def getFilename():
		resetname=current.get()
		if(os.path.isdir(current.get())):
			directory=current.get()
			filename=""
		else:
			filename=current.get().split("/")[-1]
			directory=current.get().replace(filename,"")
		current.set(tkFileDialog.askopenfilename(initialdir=directory,initialfile=filename,parent=parent,title= "Choose the file containing the filenames to convert"))
		if(current.get()!=""):
			resetname=current.get()
			parent.grid_slaves(row=0,column=2)[0].configure(relief=Tkinter.RAISED)
			parent.grid_slaves(row=0,column=3)[0].configure(relief=Tkinter.SUNKEN)
		current.set(resetname)
	return getFilename

def GetDirectoryCurry(current,parent): #Returns a 0 argument file chooser function for buttons
	def getDirectory():
		resetname=current.get()
		if(os.path.isdir(current.get())):
			directory=current.get()
		else:
			directory=current.get().replace(filename,"")
		current.set(tkFileDialog.askdirectory(initialdir=directory,parent=parent,title= "Choose the directory containing the files to convert"))
		if(current.get()!=""):
			resetname=current.get()
			parent.grid_slaves(row=0,column=2)[0].configure(relief=Tkinter.SUNKEN)
			parent.grid_slaves(row=0,column=3)[0].configure(relief=Tkinter.RAISED)
		current.set(resetname)
	return getDirectory

newformats=[]
run={}
originals={}

#BatchConverter.convertBatch(sys.argv)

def get_all_format_defaults(config, run, originals):
	for fileExtension,filetype in config.items('Formats'):
		params,params2=get_default_config(config)
		if("Default" not in run.keys()):
			run["Default"],originals["Default"]=get_default_config(config)
		if(config.has_section(filetype+'Defaults')):
			params['type']=(filetype.lower())
			for item, val in config.items(filetype+'Defaults'):
				string=StringVar()
				string.set(val)
				params[item]=string
				params2[item]=val
			if(filetype not in run.keys()):
				run[filetype],originals[filetype]=get_default_config(config)
				for item, val in config.items(filetype+'Defaults'):
					string=StringVar()
					string.set(val)
					run[filetype][item]=string
					originals[filetype][item]=val
		else:
			print "Error: Could not find config section "+filetype+'Defaults'
			continue
		if(config.has_section(fileExtension)):
			for item, val in config.items(fileExtension):
				string=StringVar()
				string.set(val)
				params[item]=string
				params2[item]=val
		params['input']=fileExtension
		params2['input']=fileExtension
		run[fileExtension]=params
		originals[fileExtension]=params2
	return run,originals

run,originals=get_all_format_defaults(config,run,originals)

FormatBox=Tkinter.Frame(Window,borderwidth=2,padx=0,relief=Tkinter.GROOVE)

formats.append(('Default',"Default"))
for item in config.options("Formats"):
	if((config.get("Formats",item),config.get("Formats",item)) not in formats):
		formats.append((config.get("Formats",item),config.get("Formats",item)))
formats.extend(config.items('Formats'))

execute=setup_format_input(FormatBox,formats)
FormatBox.grid(column=0,row=0,sticky=Tkinter.W)

def stupid():
	print "click"
create_option_editor(Window)
LocationBox=Tkinter.Frame(Window)
GetFilenameButton=Tkinter.Button(LocationBox,anchor=Tkinter.W, text="File list",command=GetFilenameCurry(top['top'],LocationBox))
GetDirectoryButton=Tkinter.Button(LocationBox,anchor=Tkinter.W, text="Directory",command=GetDirectoryCurry(top['top'],LocationBox))
SearchLabel=Tkinter.Label(LocationBox,anchor=Tkinter.W, text="Convert files found in:")
SearchLocationLabel=Tkinter.Label(LocationBox,anchor=Tkinter.W, textvariable=top['top'],bd=2,relief=Tkinter.SUNKEN,bg='white')
SearchLabel.grid(column=0,row=0,sticky=Tkinter.W)
SearchLocationLabel.grid(column=1,row=0,sticky=Tkinter.E,padx=5)
GetFilenameButton.grid(column=3,row=0,sticky=Tkinter.W)
GetDirectoryButton.grid(column=2,row=0,sticky=Tkinter.W)
LocationBox.grid(column=0,columnspan=2,row=1,sticky=Tkinter.N)

def convertall():
	stats={'conversions':0,'skipped':0,'copies':0,'errors':0}
	formats=execute.keys()
	for filetype in config.options("Formats"):
		execute[filetype][2]=execute[filetype][2].get()
		run[filetype]['top']=top['top'].get()
		for var in run[filetype].keys():
			if(isinstance(run[filetype][var],IntVar)):
				run[filetype][var]=run[filetype][var].get()
			if(isinstance(run[filetype][var],StringVar)):
				run[filetype][var]=run[filetype][var].get()
	Window.destroy()
	for filetype in config.options("Formats"):
		if(execute[filetype][2]):
			os.chdir(here)
			if('logfile' in run[filetype]):
				if(isinstance(run[filetype]['logfile'],basestring)):
					run[filetype]['logfile']=open(run[filetype]['logfile'],'a')
			if('errorfile' in run[filetype]):
				if(isinstance(run[filetype]['errorfile'],basestring)):
					run[filetype]['errorfile']=open(run[filetype]['errorfile'],'a')
			if('warningfile' in run[filetype]):
				if(isinstance(run[filetype]['warningfile'],basestring)):
					run[filetype]['warningfile']=open(run[filetype]['warningfile'],'a')
			run[filetype]['logfile'].write("Starting conversion of format: "+run[filetype]['input']+"\n")
			print "Starting conversion of format: "+run[filetype]['input']
			stats,newformats=BatchConverter.convertBatch(run[filetype],stats,formats)
			print "\rProcessed files"
			print "Conversion finished, cleaning up"
			print "...............................\n"
			for thing in set(newformats).difference(set(formats)):
				run[filetype]['logfile'].write("Detected new format: "+thing+"\n")
			run[filetype]['logfile'].write("...............................\n")
			newformats=formats
			if 'logfile' in run[filetype]:
				run[filetype]['logfile'].close()
			if 'errorfile' in run[filetype]:
				run[filetype]['errorfile'].close()
			if 'warningfile' in run[filetype]:
				run[filetype]['warningfile'].close()
	print "Formats found: "+str(set(newformats).difference(set(execute.keys())))
	print "Final stats: ",stats
MagicButton=Tkinter.Button(Window,anchor=Tkinter.S, text="Go!",command=convertall)
MagicButton.grid(column=0,columnspan=2,row=2,sticky=Tkinter.S)

while True:
	try:
		Window.update()
	except:
		break

