#! /usr/bin/env python2.6
# -*- coding: utf8 -*-

import os
import re
import xml
from xml.dom import minidom
from PIL import Image

filt = re.compile(".+[.](xml|tmx)", re.IGNORECASE)
dyesplit1 = re.compile(";")
dyesplit2 = re.compile(",")
parentDir = "../../clientdata"
iconsDir = "graphics/items/"
spritesDir = "graphics/sprites/"
errors = 0
warnings = 0
errDict = set()
safeDye = False

def printErr(err):
	errDict.add(err)
	print err

def showFileErrorById(id, rootDir, fileDir):
	print "error: id=" + id + ", file not found: " + fileDir + " (" + rootDir + fileDir + ")"

def showFileWarningById(id, rootDir, fileDir):
	print "warn: id=" + id + ", file not found: " + fileDir + " (" + rootDir + fileDir + ")"

def showError(id, text):
	print "error: id=" + id + " " + text

def showWarning(id, text):
	print "warn: id=" + id + " " + text

def showMsg(id, text, iserr):
	global errors, warnings
	if iserr == True:
		if text not in errDict:
			showError(id, text)
			errDict.add(text)
			errors = errors + 1
	else:
		if text not in errDict:
			showWarning(id, text)
			errDict.add(text)
			warnings = warnings + 1

def showMsgSprite(file, text, iserr):
	global errors, warnings
	if iserr == True:
		err = "error: sprite=" + file + " " + text
		if err not in errDict:
			printErr(err)
			errors = errors + 1
	else:
		err = "warn: sprite=" + file + " " + text
		if err not in errDict:
			printErr(err)
			warnings = warnings + 1

def showMsgFile(file, text, iserr):
	global errors, warnings
	if iserr == True:
		err = "error: file=" + file + " " + text
		if err not in errDict:
			printErr(err)
			errors = errors + 1
	else:
		err = "warn: file=" + file + " " + text
		if err not in errDict:
			printErr(err)
			warnings = warnigs + 1
	

def showFileMsgById(id, rootDir, fileDir, iserr):
	global errors, warnings
	if iserr == True:
		showFileErrorById(id, rootDir, fileDir)
		errors = errors + 1
	else:
		showFileWarningById(id, rootDir, fileDir)
		warnings = warnings + 1

def printSeparator():
	print "--------------------------------------------------------------------------------"

def showHeader():
	print "Evol client data validator"
	printSeparator()

def showFooter():
	printSeparator()
	print "Total:"
	print " Warnings: " + str(warnings)
	print " Errors:   " + str(errors)

def enumDirs(parentDir):
	global warnings, errors
	files = os.listdir(parentDir) 
	for file1 in files:
		if file1[0] == ".":
			continue
		file2 = os.path.abspath(parentDir + os.path.sep + file1)
		if not os.path.isfile(file2):
			enumDirs(file2)
		elif filt.search(file1):
			try:
				minidom.parse(file2)
			except xml.parsers.expat.ExpatError as err:
				print "error: " + file2 + ", line=" + str(err.lineno) + ", char=" + str(err.offset)
				errors = errors + 1

def loadPaths():
	global warnings
	try:
		dom = minidom.parse(parentDir + "/paths.xml")
		for node in dom.getElementsByTagName("option"):
			if node.attributes["name"].value == "itemIcons":
				iconsDir = node.attributes["value"].value
			elif node.attributes["name"].value == "sprites":
				spritesDir = node.attributes["value"].value
	except:
		print "warn: paths.xml not found"
		warnings = warnings + 1

def splitImage(image):
	try:
		idx = image.find("|")
		if idx > 0:
			imagecolor = image[idx + 1:]
			image = image[0:idx]
		else:
			imagecolor = ""
	except:
		image = ""
		imagecolor = ""
	return [image, imagecolor]

def testDye(id, color, text, iserr):
	if len(color) < 4:
		showMsg(id, "dye to small size: " + text, iserr)
		return
	colors = dyesplit1.split(color)
	for col in colors:
		if len(col) < 4:
			showMsg(id, "dye to small size: " + text, iserr)
			continue

		c = col[0];
		if col[1] != ":":
			showMsg(id, "incorrect dye string: " + text, iserr)
			continue

		if c != "R" and c != "G" and c != "B" and c != "Y" and c != "M" \
			and c != "C" and c != "W":
				showMsg(id, "incorrect dye color: " + c + " in " + text, iserr)
				continue
		if testDyeInternal(id, col[2:], text, iserr) == False:
			continue


def testDyeInternal(id, col, text, iserr):
	if col[0] != "#":
		showMsg(id, "incorrect dye colors: " + text, iserr)
		return False

	paletes = dyesplit2.split(col[1:])
	for palete in paletes:
		if len(palete) != 6:
			showMsg(id, "incorrect dye palete: " + text, iserr)
			return False
		
		for char in palete.lower():
			if (char < '0' or char > '9') and (char < 'a' or char > 'f'):
				showMsg(id, "incorrect dye palete: " + text, iserr)
				return False
	return True


def testDyeColors(id, color, text, iserr):
	if len(color) < 4:
		showMsg(id, "dye to small size: " + text, iserr)
		return -1
	colors = dyesplit1.split(color)
	for col in colors:
		if len(col) < 4:
			showMsg(id, "dye to small size: " + text, iserr)
			continue
		if testDyeInternal(id, col, text, iserr) == False:
			continue
	return len(colors)

def testDyeMark(file, color, text, iserr):
	if len(color) < 1:
		showMsgSprite(file, "dye mark size to small:" + text, iserr)
		return -1
	colors = dyesplit1.split(color)
	for c in colors:
		if len(c) != 1:
			showMsgSprite(file, "dye mark incorrect size: " + text, iserr)
			continue
		
		if c != "R" and c != "G" and c != "B" and c != "Y" and c != "M" \
			and c != "C" and c != "W":
			showMsgSprite(file, "dye make incorrect: " + text, iserr)
 			continue
	return len(colors)


def testSprites(id, node, iserr):
	try:
		tmp = node.getElementsByTagName("nosprite")
		if tmp is not None and len(tmp) > 1:
			showMsg(id, "more than one nosprite tag found", iserr)
		nosprite = True
	except:
		nosprite = False

	try:
		sprites = node.getElementsByTagName("sprite")
	except:
		sprites = None
		if nosprite == False:
			showMsg(id, "no sprite tag found", iserr)

	if sprites is not None:
		if len(sprites) == 0:
			if nosprite == False:
				showMsg(id, "no sprite tags found", iserr)
		elif len(sprites) > 3:
			showMsg(id, "incorrect number of sprite tags", iserr)
		elif len(sprites) == 1:
			file = sprites[0].childNodes[0].data
			try:
				gender = sprites[0].attributes["gender"].value
			except:
				gender = ""

			if gender != "" and gender != "unisex":
				showMsg(id, "gender tag in alone sprite", iserr)

			testSprite(id, file, iserr)
		else:
			male = False
			female = False
			for sprite in sprites:
				file = sprite.childNodes[0].data
				try:
					gender = sprite.attributes["gender"].value
				except:
					gender = ""
				if gender == "male":
					if male == True:
						showMsg(id, "double male sprite tag", iserr)
					male = True
				elif gender == "female":
					if female == True:
						showMsg(id, "double female sprite tag", iserr)
					female = True
				elif gender == "unisex":
					if female == True or male == True:
						showMsg(id, "gender sprite tag with unisex tag", False)
					male = True
					female = True
				testSprite(id, file, iserr)
			if male == False:
				showMsg(id, "no male sprite tag", iserr)
			if female == False:
				showMsg(id, "no female sprite tag", iserr)


def testSprite(id, file, iserr):
	tmp = splitImage(file)
	color = tmp[1]
	file2 = tmp[0]
	if color != "":
		dnum = testDyeColors(id, color, file, iserr)
	else:
		dnum = 0

	fullPath = os.path.abspath(parentDir + "/" + spritesDir + file2)
	if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
		showFileMsgById(id, spritesDir, file2, iserr)
	else:
		testSpriteFile(id, fullPath, file, spritesDir + file2, dnum, iserr)

def testSpriteFile(id, fullPath, file, fileLoc, dnum, iserr):
	global safeDye
	
	try:
		dom = minidom.parse(fullPath)
	except:
		return

	if len(dom.childNodes) < 1:
		return

	root = dom.childNodes[0];
	imagesets = dom.getElementsByTagName("imageset")
	if imagesets is None or len(imagesets) != 1:
		showMsgSprite(fileLoc, "incorrect number of imageset tags", iserr)
	imageset = imagesets[0]
	
	try:
		image = imageset.attributes["src"].value
		image0 = image
		img = splitImage(image)
		image = img[0]
		imagecolor = img[1]
	except:
		showMsgSprite(fileLoc, "image attribute not exist: " + image, iserr)
		return

	try:
		width = imageset.attributes["width"].value
	except:
		showMsgSprite(fileLoc, "no width attribute", iserr)
		return

	try:
		height = imageset.attributes["height"].value
	except:
		showMsgSprite(fileLoc, "no height attribute", iserr)
	
	if imagecolor != "":
		num = testDyeMark(fileLoc, imagecolor, image0, iserr)
		if safeDye == False and dnum != num:
			if dnum > num:
				e = iserr
			else:
				e = False
			showMsgSprite(fileLoc, "dye colors size not same in sprite (" + str(num) \
			+ ") and in caller (" + str(dnum) + ", id=" + str(id) + ")", e)
	elif safeDye == True and dnum > 0:
			showMsgSprite(fileLoc, "dye set in sprite but not in caller (id=" + str(id) + ")", False)


	fullPath = os.path.abspath(parentDir + "/" + image)
	if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
		showMsgSprite(fileLoc, "image file not exist: " + image, iserr)
		return
	sizes = testImageFile(image, fullPath, 0, iserr)
	s1 = int(sizes[0] / int(width)) * int(width)
	if sizes[0] != s1:
		showMsgSprite(fileLoc, "image width " + str(sizes[0]) + \
		" (need " + str(s1) + ") is not multiply to frame size " + width + ", image:" + image, False)
	s2 = int(sizes[1] / int(height)) * int(height)
	if sizes[1] != s2:
		showMsgSprite(fileLoc, "image height " + str(sizes[1]) + \
		" (need " + str(s2) + ") is not multiply to frame size " + height + ", image:" + image, False)

	num = (s1 / int(width)) * (s2 / int(height))
	if num < 1:
		showMsgSprite(fileLoc, "image have zero frames: " + iamge, iserr)

	try:
		includes = dom.getElementsByTagName("include")
	except:
		includes = None

	#todo need parse included files

	try:
		actions = dom.getElementsByTagName("action")
	except:
		actions = None

	if (actions == None or len(actions) == 0) and (includes == None or len(includes) == 0):
		showMsgSprite(fileLoc, "no actions in sprite file", iserr)
	else:
		actset = set()
		for action in actions:
			try:
				name = action.attributes["name"].value
			except:
				showMsgSprite("no action name", iserr)
				continue

			testSpriteAction(fileLoc, name, action, num, iserr)

			if name in actset:
				showMsgSprite(fileLoc, "duplicate action: " + name, iserr)
				continue
			actset.add(name)



def testSpriteAction(file, name, action, numframes, iserr):
	try:
		animations = action.getElementsByTagName("animation")
	except:
		animations = None
	
	if animations == None or len(animations) == 0:
		showMsgSprite(file, "no animation tags in action: " + name, False)

	aniset = set()
	for animation in animations:
		try:
			direction = animation.attributes["direction"].value
		except:
			direction = "default"

		if direction is aniset:
			showMsgSprite(file, "duplicate direction in action: " + name, iserr)
			continue
		aniset.add(direction)
		try:
			frames = animation.getElementsByTagName("frame")
			for frame in frames:
				try:
					idx = int(frame.attributes["index"].value)
					if idx >= numframes or idx < 0:
						showMsgSprite(file, "incorrect frame index " + str(idx) + \
						"in action: " + name, iserr)

				except:
					showMsgSprite(file, "no frame index in action: " + name, iserr)

			cnt = len(frames)
		except:
			cnt = 0

		try:
			sequences = animation.getElementsByTagName("sequence")
			cnt = cnt + len(sequences)

			for sequence in sequences:
				try:
					i1 = int(sequence.attributes["start"].value)
					i2 = int(sequence.attributes["end"].value)
					if i1 >= numframes or i1 < 0:
						showMsgSprite(file, "incorrect start sequence index " + str(i1) + \
						"in action: " + name, iserr)
					if i2 >= numframes or i2 < 0:
						showMsgSprite(file, "incorrect end sequence index " + str(i2) + \
						"in action: " + name, iserr)
				except:
					showMsgSprite(file, "no sequence start or end index in action: " + name, iserr)
		except:
			None

		if cnt == 0:
			showMsgSprite(file, "no frames or sequences in action: " + name, iserr)

	if "default" not in aniset:
		if "down" not in aniset:
			showMsgSprite(file, "no down direction in animation: " + name, iserr)
		if "up" not in aniset:
			showMsgSprite(file, "no up direction in animation: " + name, iserr)
		if "left" not in aniset:
			showMsgSprite(file, "no left direction in animation: " + name, iserr)
		if "right" not in aniset:
			showMsgSprite(file, "no right direction in animation: " + name, iserr)

	if name == "dead" and len(animations) > 0:
		lastani = animations[len(animations) - 1]
		lastNode = None
		nc = 0
		for node in lastani.childNodes:
			if node.nodeName == "frame":
				lastNode = node
				nc = nc + 1
			if node.nodeName == "sequence":
				lastNode = node
				nc = nc + 2
		if nc > 1:
			try:
				delay = int(lastNode.attributes["delay"].value)
			except:
				delay = 0
			if delay > 0 and delay < 5000:
				showMsgSprite(file, "last frame\sequence in dead animation have to low limit. Need zero or >5000: " + name, iserr)




def testImageFile(file, fullPath, sz, iserr):
	try:
		img = Image.open(fullPath, "r")
		img.load()
	except:
		showMsgFile(file, "incorrect image format", iserr)
		return

	if img.format != "PNG":
		showMsgFile(file, "image format is not png", False)

	sizes = img.size
	if sz != 0:
		if sizes[0] > sz or sizes[1] > sz:
			showMsgFile(file, "image size incorrect (" + str(sizes[0]) \
			+ "x" + str(sizes[1]) + ") should be (" + str(sz) + "x" \
			+ str(sz) + ")", iserr)
	
	return sizes	


def testItems(fileName, imgDir):
	global warnings, errors, safeDye
	print "Checking items.xml"
	dom = minidom.parse(parentDir + fileName)
	idset = set()
	for node in dom.getElementsByTagName("item"):
		id = node.attributes["id"].value
		if id in idset:
			print "error: duplicated id=" + id
			errors = errors + 1
		else:
			idset.add(id)
			
		idI = int(id)
		try:
			type = node.attributes["type"].value
		except:
			type = ""
			print "warn: no type attribute for id=" + id
			warnings = warnings + 1
		try:
			image = node.attributes["image"].value
			image0 = image
			img = splitImage(image)
			image = img[0]
			imagecolor = img[1]
		except:
			image = ""
			image0 = ""
			imagecolor = ""

		if type == "hairsprite":
			if idI >= 0:
				print "error: hairsprite with id=" + id
				errors = errors + 1
			elif idI < -100:
				print "error: hairsprite override player sprites"
				errors = errors + 1

			safeDye = True
			testSprites(id, node, True)
			safeDye = False

		elif type == "racesprite":
			if idI >= 0:
				print "error: racesprite with id=" + id
				errors = errors + 1
			elif idI > -100:
				print "error: racesprite override player hair"
				errors = errors + 1
		elif type == "usable" or type == "unusable" or type == "generic" \
		or type == "equip-necklace" or type == "equip-torso" or type == "equip-feet" \
		or type == "equip-arms" or type == "equip-legs" or type == "equip-head" \
		or type == "equip-shield" or type == "equip-1hand" or type == "equip-2hand" \
		or type == "equip-charm" or type == "equip-ammo" or type == "equip-neck" \
		or type == "equip-ring":
			if image == "":
				print "error: missing image attribute on id=" + id
				errors = errors + 1
				continue
			elif len(imagecolor) > 0:
				testDye(id, imagecolor, "image=" + image0, True)


			fullPath = os.path.abspath(parentDir + "/" + imgDir + image)
			if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
				showFileErrorById (id, imgDir, image)
				errors = errors + 1
			else:
				testImageFile(imgDir + image, fullPath, 32, True)

			if type != "usable" and type != "unusable" and type != "generic" \
			and type != "equip-necklace" and type != "equip-1hand" \
			and type != "equip-2hand" and type != "equip-ammo" \
			and type != "equip-charm" and type != "equip-neck":
				err = type != "equip-shield"
				testSprites(id, node, err)
		elif type == "other":
			None
		elif type != "":
			print "warn: unknown type '" + type + "' for id=" + id
			warnings = warnings + 1

showHeader()
print "Checking xml file syntax"
enumDirs(parentDir)
loadPaths()
testItems("/items.xml", iconsDir)
showFooter()
