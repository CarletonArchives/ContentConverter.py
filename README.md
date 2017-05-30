# ContentConverter.py
This program requires the following be installed:

ffmpeg:
If the site is down, and you are on a mac, try installing homebrew first, and then run brew install ffmpeg in a terminal

ImageMagick

GhostScript: can be tested by typing gs into a terminal.

Usage: python ContentConverter.py (Folder)

The program will convert all of the formats as defined in the config. It will try to place items in a DIPS folder if they begin within the originals folder. It will also ignore anything in a folder named meta. It also maintains folder structure, and should create various logs (FullLog.txt, FullErrors.txt) to wherever the program is located.

Edit the ContentConverterConfig.cfg file to see what settings are modifiable. 
To create quicktime compatible videos, add "-pix_fmt yuv420p" to extra_args in the config, and possibly also "-vcodec libx264"

It converts format by format, not folder by folder (although it can be run on any individual folder).
