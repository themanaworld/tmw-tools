#! /usr/bin/env python2.6
# -*- coding: utf8 -*-
#
# Copyright (C) 2010-2011  Evol Online
# Author: Andrei Karas (4144)

import array
import base64
import gzip
import os
import re
import datetime
import xml
import ogg.vorbis
from xml.dom import minidom
from PIL import Image
import zlib

filt = re.compile(".+[.](xml|tmx|tsx)", re.IGNORECASE)
filtmaps = re.compile(".+[.]tmx", re.IGNORECASE)
filtimages = re.compile(".+[.]png", re.IGNORECASE)
filtxmls = re.compile(".+[.]xml", re.IGNORECASE)
filtogg = re.compile(".+[.]ogg", re.IGNORECASE)
dyesplit1 = re.compile(";")
dyesplit2 = re.compile(",")
parentDir = "../../gittorious/clientdata-beta"
iconsDir = "graphics/items/"
spritesDir = "graphics/sprites/"
particlesDir = "graphics/particles/"
sfxDir = "sfx/"
musicDir = "music/"
mapsDir = "maps/"
attackSfxFile = "fist-swish.ogg"
spriteErrorFile = "error.xml"
levelUpEffectFile = "levelup.particle.xml"
portalEffectFile = "warparea.particle.xml"
minimapsDir = "graphics/minimaps/"
wallpapersDir = "graphics/images/"
wallpaperFile = "login_wallpaper.png"
errors = 0
warnings = 0
errDict = set()
safeDye = False
borderSize = 20
colorsList = set()

testBadCollisions = False
# number of tiles difference. after this amount tiles can be counted as incorrect
tileNumDiff = 3
# max number of incorrect tiles. If more then tile not counted as error
maxNumErrTiles = 5

class Tileset:
	None

class Layer:
	None

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

def showMsg(id, text, src, iserr):
	global errors, warnings
	if text != "":
		text = text + ", " + src
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
			warnings = warnings + 1
	

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
	print "Evol client data validator."
	print "Run at: " + datetime.datetime.now().isoformat()
	print "http://www.gitorious.org/evol/evol-tools/blobs/master/testxml/testxml.py"
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
		else:
			if filt.search(file1):
				try:
					minidom.parse(file2)
				except xml.parsers.expat.ExpatError as err:
					print "error: " + file2 + ", line=" + str(err.lineno) + ", char=" + str(err.offset)
					errors = errors + 1
			if file1 != "testxml.py":
				checkFilePermission(file2)

def checkFilePermission(fullName):
	if os.access(fullName, os.X_OK):
		print "warn: execute flag on file: " + fullName


def loadPaths():
	global warnings, iconsDir, spritesDir, sfxDir, particlesDir, mapsDir, attackSfxFile, spriteErrorFile, \
			levelUpEffectFile, portalEffectFile, minimapsDir, wallpapersDir, walpaperFile, \
			musicDir
	try:
		dom = minidom.parse(parentDir + "/paths.xml")
		for node in dom.getElementsByTagName("option"):
			if node.attributes["name"].value == "itemIcons":
				iconsDir = node.attributes["value"].value
				if iconsDir != "graphics/items/":
					print "warn: itemIcons path has not default value."\
							" Will be incampatible with old clients."
			elif node.attributes["name"].value == "sprites":
				spritesDir = node.attributes["value"].value
				if spritesDir != "graphics/sprites/":
					print "warn: sprites path has not default value."\
							" Will be incampatible with old clients."
			elif node.attributes["name"].value == "sfx":
				sfxDir = node.attributes["value"].value

			elif node.attributes["name"].value == "particles":
				particlesDir = node.attributes["value"].value
				if particlesDir != "graphics/particles/":
					print "warn: particles path has not default value."\
							" Will be incampatible with old clients."
			elif node.attributes["name"].value == "maps":
				mapsDir = node.attributes["value"].value
				if mapsDir != "maps/":
					print "warn: maps path has not default value."\
							" Will be incampatible with old clients."
			elif node.attributes["name"].value == "attackSfxFile":
				attackSfxFile = node.attributes["value"].value
			elif node.attributes["name"].value == "spriteErrorFile":
				spriteErrorFile = node.attributes["value"].value
			elif node.attributes["name"].value == "levelUpEffectFile":
				levelUpEffectFile = node.attributes["value"].value
			elif node.attributes["name"].value == "portalEffectFile":
				portalEffectFile = node.attributes["value"].value
			elif node.attributes["name"].value == "minimaps":
				minimapsDir = node.attributes["value"].value
			elif node.attributes["name"].value == "wallpapers":
				wallpapersDir = node.attributes["value"].value
			elif node.attributes["name"].value == "wallpaperFile":
				wallpaperFile = node.attributes["value"].value
			elif node.attributes["name"].value == "music":
				musicDir = node.attributes["value"].value
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

def testDye(id, color, text, src, iserr):
	if len(color) < 4:
		showMsg(id, "dye to small size: " + text, src, iserr)
		return
	colors = dyesplit1.split(color)
	for col in colors:
		if len(col) < 4:
			showMsg(id, "dye to small size: " + text, src, iserr)
			continue

		c = col[0];
		if col[1] != ":":
			showMsg(id, "incorrect dye string: " + text, src, iserr)
			continue

		if c != "R" and c != "G" and c != "B" and c != "Y" and c != "M" \
			and c != "C" and c != "W" and c != "S":
				showMsg(id, "incorrect dye color: " + c + " in " + text, src, iserr)
				continue
		if testDyeInternal(id, col[2:], text, src, iserr) == False:
			continue


def testDyeInternal(id, col, text, src, iserr):
	if col[0] != "#":
		showMsg(id, "incorrect dye colors: " + text, src, iserr)
		return False

	paletes = dyesplit2.split(col[1:])
	for palete in paletes:
		if len(palete) != 6:
			showMsg(id, "incorrect dye palete: " + text, src, iserr)
			return False
		
		for char in palete.lower():
			if (char < '0' or char > '9') and (char < 'a' or char > 'f'):
				showMsg(id, "incorrect dye palete: " + text, src, iserr)
				return False
	return True


def testDyeColors(id, color, text, src, iserr):
	if len(color) < 4:
		showMsg(id, "dye to small size: " + text, src, iserr)
		return -1
	colors = dyesplit1.split(color)
	for col in colors:
		if len(col) < 4:
			showMsg(id, "dye to small size: " + text, src, iserr)
			continue
		if testDyeInternal(id, col, text, src, iserr) == False:
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
			and c != "C" and c != "W" and c != "S":
			showMsgSprite(file, "dye make incorrect: " + text, iserr)
 			continue
	return len(colors)


def testSprites(id, node, checkGender, isNormalDye, isMust, checkAction, iserr):
	try:
		tmp = node.getElementsByTagName("nosprite")
		if tmp is not None and len(tmp) > 1:
			showMsg(id, "more than one nosprite tag found", "", iserr)
		nosprite = True
	except:
		nosprite = False

	if isMust == False:
		nosprite = True

	try:
		sprites = node.getElementsByTagName("sprite")
	except:
		sprites = None
		if nosprite == False:
			showMsg(id, "no sprite tag found", "", iserr)

	if sprites is not None:
		if len(sprites) == 0:
			if nosprite == False:
				showMsg(id, "no sprite tags found", "", iserr)
		elif len(sprites) > 3 and checkGender:
			showMsg(id, "incorrect number of sprite tags", "", iserr)
		elif len(sprites) == 1:
			file = sprites[0].childNodes[0].data
			if checkGender:
				try:
					gender = sprites[0].attributes["gender"].value
				except:
					gender = ""

				if gender != "" and gender != "unisex":
					showMsg(id, "gender tag in alone sprite", "", iserr)

			try:
				variant = int(sprites[0].attributes["variant"].value)
			except:
				variant = 0

			testSprite(id, file, variant, isNormalDye, checkAction, iserr)
		else:
			male = False
			female = False
			unisex = False
			for sprite in sprites:
				file = sprite.childNodes[0].data
				if checkGender:
					try:
						gender = sprite.attributes["gender"].value
					except:
						gender = ""
					if gender == "male":
						if male == True:
							showMsg(id, "double male sprite tag", "", iserr)
						male = True
					elif gender == "female":
						if female == True:
							showMsg(id, "double female sprite tag", "", iserr)
						female = True
					elif gender == "unisex":
						unisex = True
				try:
					variant = int(sprite.attributes["variant"].value)
				except:
					variant = 0
				testSprite(id, file, variant, isNormalDye, checkAction, iserr)
			if checkGender:
				if male == False and unisex == False:
					showMsg(id, "no male sprite tag", "",iserr)
				if female == False and unisex == False:
					showMsg(id, "no female sprite tag", "", iserr)
				if unisex == True and female == True and male == True:
					showMsg(id, "gender sprite tag with unisex tag", "", iserr)
				if unisex == False and male == False and female == False:
					showMsg(id, "no any gender tags", "", iserr)
	

def testSprite(id, file, variant, isNormalDye, checkAction, iserr):
	global safeDye
	tmp = splitImage(file)
	color = tmp[1]
	file2 = tmp[0]
	if color != "":
		dnum = testDyeColors(id, color, file, "", iserr)
	else:
		dnum = 0

	fullPath = os.path.abspath(parentDir + "/" + spritesDir + file2)
	if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
		showFileMsgById(id, spritesDir, file2, iserr)
	else:
		if not isNormalDye and color is not None and len(color) > 0:
			showMsg(id, "sprite tag have dye string but it should not, because used colors dye", color, iserr)

		oldSafe = safeDye
		safeDye = True
		testSpriteFile(id, fullPath, file, spritesDir + file2, dnum, variant, checkAction, iserr)
		safeDye = oldSafe

def powerOfTwo(num):
	val = 1
	while val < num:
		val = val * 2
	return val

def testSpriteFile(id, fullPath, file, fileLoc, dnum, variant, checkAction, iserr):
	global safeDye
	
	try:
		dom = minidom.parse(fullPath)
	except:
		return

	if len(dom.childNodes) < 1:
		return

	try:
		variants = dom.documentElement.attributes["variants"].value
	except:
		variants = 0

	try:
		variant_offset = dom.documentElement.attributes["variant_offset"].value
	except:
		variant_offset = 0
		
	root = dom.childNodes[0];
	imagesets = dom.getElementsByTagName("imageset")
	if imagesets is None or len(imagesets) < 1:
		showMsgSprite(fileLoc, "incorrect number of imageset tags", iserr)
		return
	isets = set()
	imagesetnums = dict()
	num = 0
	for imageset in imagesets:
		try:
			name = imageset.attributes["name"].value
		except:
			showMsgSprite(fileLoc, "imageset don't have name attribute", iserr)
			name = None
			
		if name is not None:
			if name in isets:
				showMsgSprite(fileLoc, "imageset with name '" + name + "' already exists", iserr)
			isets.add(name)
			
		image = ""
		try:
			image = imageset.attributes["src"].value
			image0 = image
			img = splitImage(image)
			image = img[0]
			imagecolor = img[1]
		except:
			showMsgSprite(fileLoc, "image attribute not exist: " + image, iserr)
			continue

		try:
			width = imageset.attributes["width"].value
		except:
			showMsgSprite(fileLoc, "no width attribute", iserr)
			continue

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
			continue
		sizes = testImageFile(image, fullPath, 0, " " + fileLoc, iserr)
		s1 = int(sizes[0] / int(width)) * int(width)

		sizesOGL = [0,1]
		sizesOGL[0] = powerOfTwo(sizes[0])
		sizesOGL[1] = powerOfTwo(sizes[1])

		if s1 == 0:
			tmp = int(width)
		else:
			tmp = s1
		if sizes[0] != s1 and tmp != sizesOGL[0]: 
			showMsgSprite(fileLoc, "image width " + str(sizes[0]) + \
			" (need " + str(tmp) + ") is not multiply to frame size " + width + ", image:" + image, False)

		if sizes[0] != sizesOGL[0]:
			if sizesOGL[0] > sizes[0]:
				txt = str(sizesOGL[0] / 2) + " or "
			else:
				txt = ""

			showMsgSprite(fileLoc, "image width should be power of two. If not some pixels can be"\
				" lost in OpenGL mode.\nCurrent image width " + str(sizes[0]) + \
				". used in sprite width " + str(tmp) +
				"\nallowed width " + txt + str(sizesOGL[0]) + " (" + image + ")", False)
	
		s2 = int(sizes[1] / int(height)) * int(height)

		if s2 == 0:
			tmp = int(height)
		else:
			tmp = s2;

		if sizes[1] != s2 and tmp != sizesOGL[1]:
			showMsgSprite(fileLoc, "image height " + str(sizes[1]) + \
			" (need " + str(tmp) + ") is not multiply to frame size " + height + ", image:" + image, False)

		if sizes[1] != sizesOGL[1]:
			if sizesOGL[1] > sizes[1]:
				txt = str(sizesOGL[1] / 2) + " or "
			else:
				txt = ""

			showMsgSprite(fileLoc, "image height should be power of two. If not some pixels can be"\
				" lost in OpenGL mode.\nCurrent image height " + str(sizes[1]) + \
				". used in sprite height " + str(tmp) +
				"\nallowed height " + txt + str(sizesOGL[1]) + " (" + image + ")", False)


		num = (s1 / int(width)) * (s2 / int(height))
		if variants == 0 and variant > 0:
			showMsgSprite(fileLoc, "missing variants attribute in sprite", iserr)
		if variants > 0 and variant >= variants:
			showMsgSprite(fileLoc, "variant number more then in variants attribute", iserr)

		if variant > 0 and variant >= num:
			showMsgSprite(fileLoc, "to big variant number " + str(variant) \
			+ ". Frames number " + str(num) + ", id=" + str(id), iserr)
		if num < 1:
			showMsgSprite(fileLoc, "image have zero frames: " + image, iserr)
		if name is not None and num > 0:
			imagesetnums[name] = num

	try:
		includes = dom.getElementsByTagName("include")
		for include in includes:
			try:
				incfile = include.attributes["file"].value
				file2 = os.path.abspath(parentDir + os.path.sep + spritesDir + incfile)
				if not os.path.isfile(file2):
					showMsgSprite(fileLoc, "include file not exists " + incfile, True)
			except:
				showMsgSprite(fileLoc, "bad include", iserr)


	except:
		includes = None

	#todo need parse included files

	try:
		actions = dom.getElementsByTagName("action")
	except:
		actions = None

	foundAction = False

	if (actions == None or len(actions) == 0) and (includes == None or len(includes) == 0):
		showMsgSprite(fileLoc, "no actions in sprite file", iserr)
	else:
		actset = set()
		frameSet = set()
		for action in actions:
			try:
				name = action.attributes["name"].value
			except:
				showMsgSprite("no action name", iserr)
				continue
			try:
				setname = action.attributes["imageset"].value
			except:
				setname = ""
			if setname in imagesetnums:
				num = imagesetnums[setname]
			else:
				num = 0
				showMsgSprite(fileLoc, "using incorrect imageset name in action: " + name, iserr)
			frameSet = frameSet | testSpriteAction(fileLoc, name, action, num, iserr)

			if name in actset:
				showMsgSprite(fileLoc, "duplicate action: " + name, iserr)
				continue
			actset.add(name)

		if len(frameSet) > 0:
			errIds = ""
			i = 0
			while i < max(frameSet):
				if i not in frameSet:
					errIds = errIds + str(i) + ","
				i = i + 1
			if len(errIds) > 0:
				showMsgSprite(fileLoc, "unused frames: " + errIds[0:len(errIds)-1], False)

	if checkAction != "" and checkAction not in actset:
		showMsgSprite(fileLoc, "no attack action '" + checkAction + "' in sprite", iserr)


def testSpriteAction(file, name, action, numframes, iserr):
	framesid = set()
	
	try:
		animations = action.getElementsByTagName("animation")
	except:
		animations = None
	
	if animations == None or len(animations) == 0:
		if name != "default":
			showMsgSprite(file, "no animation tags in action: " + name, False)
		else:
			return framesid

	aniset = set()
	delayTags = ("frame", "sequence", "pause")

	for animation in animations:
		try:
			direction = animation.attributes["direction"].value
		except:
			direction = "default"

		if direction is aniset:
			showMsgSprite(file, "duplicate direction in action: " + name, iserr)
			continue
		aniset.add(direction)

		lastIndex1 = -1
		lastIndex2 = -1
		lastOffsetX = 0
		lastOffsetY = 0
		cnt = 0
		labels = set()

		for node2 in animation.childNodes:
			if node2.nodeName in delayTags:
				try:
					delay = int(node2.attributes["delay"].value)
				except:
					delay = 0

				if delay % 10 != 0:
					showMsgSprite(file, "delay " + str(delay) + " must be multiple of 10 in action: " + name + \
							", direction: " + direction, False)


			if node2.nodeName == "frame" or node2.nodeName == "sequence":
				try:
					offsetX = int(node2.attributes["offsetX"].value)
				except:
					offsetX = 0
				try:
					offsetY = int(node2.attributes["offsetY"].value)
				except:
					offsetY = 0

			if node2.nodeName == "frame":
				frame = node2	
				try:
					idx = int(frame.attributes["index"].value)
				except:
					showMsgSprite(file, "no frame index in action: " + name, iserr)
					
				if idx >= numframes or idx < 0:
					showMsgSprite(file, "incorrect frame index " + str(idx) + \
							" action: " + name + ", direction: "\
							+ direction, iserr)
				else:
					framesid.add(idx)
				if lastIndex1 == idx and lastIndex2 == -1 and offsetX == lastOffsetX \
				and offsetY == lastOffsetY:
					showMsgSprite(file, "duplicate frame animation for frame index=" \
							+ str(idx) + " action: " + name + \
							", direction: " + direction + "\n" + node2.toxml(), False)
					#print node2.toxml()
				else:
					lastIndex1 = idx
					lastIndex2 = -1
					lastOffsetX = offsetX
					lastOffsetY = offsetY

				framesid.add(idx)
				cnt = cnt + 1
			elif node2.nodeName == "sequence":
				sequence = node2
				try:
					sframes = dyesplit2.split(sequence.attributes["value"].value)
				except:
					sframes = None
				if sframes is not None:
					for frm in sframes:
						if frm != "p":
							k = frm.find("-")
							if k == 0 or k == len(frm) - 1:
								showMsgSprite(file, "incorrect sequence value " + \
										name + ", direction: " + direction, iserr)
							elif k == -1:
								#same as frame
								idx = int(frm)
								if idx >= numframes or idx < 0:
									showMsgSprite(file, "incorrect frame index " + str(idx) + \
											" action: " + name + ", direction: "\
											+ direction, iserr)
								else:
									framesid.add(idx)
							else:
								#same as simple sequence
								i1 = int(frm[:k])
								i2 = int(frm[k + 1:])
								if i1 >= numframes or i1 < 0:
									showMsgSprite(file, "incorrect start sequence index " + str(i1) + \
										" action: " + name + ", direction: " + direction, iserr)
								if i2 >= numframes or i2 < 0:
									showMsgSprite(file, "incorrect end sequence index " + str(i2) + \
										" action: " + name + ", direction: " + direction, iserr)
								if i1 == i2:
									showMsgSprite(file, "start and end sequence index is same. " \
										+ "May be better use frame? action: " + \
										name + ", direction: " + direction, False)

								for i in range(i1,i2 + 1):
									framesid.add(i)
					cnt = cnt + 1
					continue
				
				try:
					i1 = int(sequence.attributes["start"].value)
					i2 = int(sequence.attributes["end"].value)
				except:
					showMsgSprite(file, "no sequence start or end index action: " + \
							name + ", direction: " + direction, iserr)
				try:
					repeat = int(sequence.attributes["repeat"].value)
				except:
					repeat = 1
					
				if i1 >= numframes or i1 < 0:
					showMsgSprite(file, "incorrect start sequence index " + str(i1) + \
							" action: " + name + ", direction: " + direction, iserr)
				if i2 >= numframes or i2 < 0:
					showMsgSprite(file, "incorrect end sequence index " + str(i2) + \
							" action: " + name + ", direction: " + direction, iserr)
				if i1 == i2:
					showMsgSprite(file, "start and end sequence index is same. " \
							+ "May be better use frame? action: " + \
							name + ", direction: " + direction, False)

				if lastIndex1 == i1 and lastIndex2 == i2 and offsetX == lastOffsetX \
				and offsetY == lastOffsetY:
					showMsgSprite(file, "duplicate sequence animation. May be need use repeat attribue? for start=" \
							+ str(i1) + ", end=" + str(i2) + " action: " + \
							name + ", direction: " + direction + "\n" + node2.toxml(), False)
				else:
					lastIndex1 = i1
					lastIndex2 = i2
					lastOffsetX = offsetX
					lastOffsetY = offsetY
			
				cnt = cnt + 1
				for i in range(i1,i2 + 1):
					framesid.add(i)
			elif node2.nodeName == "end" or node2.nodeName == "jump" or node2.nodeName == "label" or node2.nodeName == "goto":
				lastIndex1 = -1
				lastIndex2 = -1
				lastOffsetX = 0
				lastOffsetY = 0
				cnt = cnt + 1
			elif node2.nodeName == "pause":
				try:
					delay = int(node2.attributes["delay"].value)
				except:
					delay = 0
				if delay <= 0:
					showMsgSprite(file, "incorrect delay in pause tag " + name, iserr)

			elif node2.nodeName == "#text" or node2.nodeName == "#comment":
				None
			else:
				showMsgSprite(file, "unknown animation tag: " + node2.nodeName + ", " + name, False)

			if node2.nodeName == "jump":
				try:
					jaction = node2.attributes["action"].value
				except:
					jaction = ""
				if jaction == "" or jaction is None:
					showMsgSprite(file, "no action attribute in jump tag " + name, iserr)
			elif node2.nodeName == "label":
				try:
					label = node2.attributes["name"].value
				except:
					label = ""
				if label == "" or label is None:
					showMsgSprite(file, "no name attribute in label tag " + name, iserr)
				else:
					if label in labels:
						showMsgSprite(file, "duplicate label " + label + " " + name + "\n" \
							+ node2.toxml(), iserr)
					else:
						labels.add(label)
			elif node2.nodeName == "goto":
				try:
					label = node2.attributes["label"].value
				except:
					label = ""
				if label == "" or label is None:
					showMsgSprite(file, "no label attribute in goto tag " + name, iserr)
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
				cont = int(lastNode.attributes["continue"].value)
			except:
				cont  = 0;
			if cont == 0:
				try:
					delay = int(lastNode.attributes["delay"].value)
				except:
					delay = 0
				if delay > 0 and delay < 5000:
					showMsgSprite(file, "last frame\sequence in dead animation have to low limit. Need zero or >5000: " + name, False)

	return framesid


def testImageFile(file, fullPath, sz, src, iserr):
	try:
		img = Image.open(fullPath, "r")
		img.load()
	except:
		showMsgFile(file, "incorrect image format" + src, iserr)
		return

	if img.format != "PNG":
		showMsgFile(file, "image format is not png" + src, False)

	sizes = img.size
	if sz != 0:
		if sizes[0] > sz or sizes[1] > sz:
			showMsgFile(file, "image size incorrect (" + str(sizes[0]) \
			+ "x" + str(sizes[1]) + ") should be (" + str(sz) + "x" \
			+ str(sz) + ")", iserr)
		elif sizes[0] < sz or sizes[1] < sz:
			showMsgFile(file, "possible image size incorrect (" + str(sizes[0]) \
			+ "x" + str(sizes[1]) + ") should be (" + str(sz) + "x" \
			+ str(sz) + ")", False)

				

	return sizes	

def testSound(file, sfxDir):
	fullPath = parentDir + "/" + sfxDir + file
	if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
		print "error:" + fullPath
		showMsgFile(file, "sound file not found", True)
		return
	try:
		snd = ogg.vorbis.VorbisFile(fullPath)
	except ogg.vorbis.VorbisError as e:
		showMsgFile(file, "sound file incorrect error: " + str(e), True)


def testParticle(id, file, src):
	fullPath = parentDir + "/" + file
	if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
		showMsgFile(file, "particle file not found", True)
		return
	try:
		dom = minidom.parse(fullPath)
	except:
		showMsgFile(file, "incorrect particle xml file", True)
		return

	nodes = dom.getElementsByTagName("particle")
	if len(nodes) < 1:
		showMsgFile(file, "missing particle tags", False)
	else:
		for node in nodes:
			testEmitters(id, file, node, file)


def testEmitters(id, file, parentNode, src):
	for node in parentNode.getElementsByTagName("property"):
		try:
			name = node.attributes["name"].value
		except:
			showMsgFile(file, "missing attribute name in emitter" \
					" in particle file", True)
			continue
		try:
			value = node.attributes["value"].value
		except:
			value = None

		if name == "image":
			if value == None:
				showMsgFile(file, "missing attribute value in emitter" \
						" image attribute", True)
			img = splitImage(value)
			image = img[0]
			imagecolor = img[1]
			if imagecolor != None and len(imagecolor) > 0:
				testDye(id, imagecolor, "image=" + image, src, True)
			fullName = parentDir + "/" + image
			if not os.path.isfile(fullName) or os.path.exists(fullName) == False:
				showMsgFile(file, "image file not exist: " + image, True)
			else:
				testImageFile(image, fullName, 0, " " + file,True)
	for node in parentNode.getElementsByTagName("emitter"):
		testEmitters(id, file, node, src)



def testItems(fileName, imgDir):
	global warnings, errors, safeDye
	print "Checking items.xml"
	dom = minidom.parse(parentDir + fileName)
	idset = set()
	oldId = None
	for node in dom.getElementsByTagName("item"):
		if node.parentNode != dom.documentElement:
			continue

		try:
			id = node.attributes["id"].value
		except:
			if oldId is None:
				print "error: item without id"
			else:
				print "error: item without id. Last id was: " + oldId
			errors = errors + 1
			continue
		oldId = id
		if id in idset:
			print "error: duplicated id=" + id
			errors = errors + 1
		else:
			idset.add(id)
			
		idI = int(id)

		try:
			colors = node.attributes["colors"].value
		except:
			colors = None


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

		try:
			floor = node.attributes["floor"].value
			floor0 = floor
			flr = splitImage(floor)
			floor = flr[0]
			floorcolor = flr[1]
		except:
			floor = None
			floor0 = None
			floorcolor = None

		try:
			description = node.attributes["description"].value
		except:
			description = ""

		try:
			missile = node.attributes["missile-particle"].value
		except:
			missile = ""

		try:
			drawBefore = node.attributes["drawBefore"].value
		except:
			drawBefore = ""

		try:
			drawAfter = node.attributes["drawAfter"].value
		except:
			drawAfter = ""

		try:
			drawPriority = int(node.attributes["drawPriority"].value)
		except:
			drawPriority = 0
			

		if type == "hairsprite":
			if idI >= 0:
				print "error: hairsprite with id=" + id
				errors = errors + 1
			elif idI < -100:
				print "error: hairsprite override player sprites"
				errors = errors + 1

			safeDye = True
			testSprites(id, node, True, True, True, "", True)
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
				if colors is None:
					testDye(id, imagecolor, "image=" + image0, "items.xml", True)
				else:
					testDyeMark(id, imagecolor, "image=" + image0, True)
					if colors not in colorsList:
						print "error: colors value " + colors + " not found in itemcolors.xml"
						errors = errors + 1

			if floorcolor != None and len(floorcolor) > 0:
				if colors is None:
					testDye(id, floorcolor, "floor=" + floor0, "items.xml", True)
				else:
					testByeMark(id, imagecolor, "floor=" + floor0, True);
					if colors not in colorsList:
						print "error: colors value " + colors + " not found in itemcolors.xml"
						errors = errors + 1

			if description == "":
				print "warn: missing description attribute on id=" + id
				warnings = warnings + 1
			if missile != "":
				testParticle(id, missile, "items.xml")

			testSounds(id, node, "item")

			try:
				floorSprite = node.getElementsByTagName("floor")[0]
			except:
				floorSprite = None
			if floorSprite != None:
				if floor != None:
					print "error: found attribute floor and tag floor. " + \
							"Should be only one tag or attribute. id=" + id
					errors = errors + 1
				testSprites(id, floorSprite, False, colors is None, True, "", err)

			fullPath = os.path.abspath(parentDir + "/" + imgDir + image)
			if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
				showFileErrorById (id, imgDir, image)
				errors = errors + 1
			else:
				testImageFile(imgDir + image, fullPath, 32, "", True)

			if floor != None:
				fullPath = os.path.abspath(parentDir + "/" + imgDir + floor)
				if not os.path.isfile(fullPath) or os.path.exists(fullPath) == False:
					showFileErrorById (id, imgDir, floor)
					error = errors + 1
				else:
					testImageFile(imgDir + floor, fullPath, 0, "", True)

			testItemReplace(id, node, "replace")
			if drawBefore != "":
				checkSpriteName(id, drawBefore)
			if drawAfter != "":
				checkSpriteName(id, drawAfter)

			try:
				attackaction = node.attributes["attack-action"].value
			except:
				attackaction = ""

			testSprites(id, node, True, colors is None, False, attackaction, True)

			if type != "usable" and type != "unusable" and type != "generic" \
			and type != "equip-necklace" and type != "equip-1hand" \
			and type != "equip-2hand" and type != "equip-ammo" \
			and type != "equip-charm" and type != "equip-neck":
				err = type != "equip-shield"
				testSprites(id, node, True, colors is None, True, "", err)
		elif type == "other":
			None
		elif type != "":
			print "warn: unknown type '" + type + "' for id=" + id
			warnings = warnings + 1


def testItemReplace(id, rootNode, name):
	global warnings, errors
	sprites = set()
	for node in rootNode.getElementsByTagName(name):
		if node.parentNode != rootNode:
			continue
		try:
			sprite = node.attributes["sprite"].value
		except:
			print "error: reading replace sprite name, id=" + str(id)
			continue
		checkSpriteName(id, sprite)
		for itemNode in node.getElementsByTagName("item"):
			if itemNode.parentNode != node:
				continue
			#TODO here need check "from" and "to" for correct item id


def checkSpriteName(id, name):
	global warnings, errors
	if name != "shoes" and name != "boot" and name != "boots" and name != "bottomclothes" \
			and name != "bottom" and name != "pants" and name != "topclothes" and \
			name != "top" and name != "torso" and name != "body" and name != "misc1" \
			and name != "misc2" and name != "scarf" and name != "scarfs" and \
			name != "hair" and name != "hat" and name != "hats" and name != "wings" \
			and name != "glove" and name != "gloves" and name != "weapon" and \
			name != "weapons" and name != "shield" and name != "shields" and \
			name != "amulet" and name != "amulets" and name != "ring" and name != "rings":
				print "error: unknown sprite name " + name + ", id=" + str(id)


def testMonsters(fileName):
	global warnings, errors
	print "Checking monsters.xml"
	dom = minidom.parse(parentDir + fileName)
	idset = set()
	for node in dom.getElementsByTagName("monster"):
		try:
			id = node.attributes["id"].value
		except:
			print "error: no id for monster"
			errors = errors + 1
			continue

		if id in idset:
			print "duplicate id=" + id
		else:
			idset.add(id)

		try:
			name = node.attributes["name"].value
		except:
			print "error: no name for id=" + id
			errors = errors + 1
			name = ""

		testTargetCursor(id, node, fileName)
		testSprites(id, node, False, True, True, "", True)
		testSounds(id, node, "monster")
		testParticles(id, node, "particlefx", fileName)


def testTargetCursor(id, node, file):
	try:
		targetCursor = node.attributes["targetCursor"].value
		if targetCursor != "small" and targetCursor != "medium" and targetCursor != "large":
			showMsgFile(id, "unknown target cursor " + targetCursor)
	except:
		None

def testParticles(id, node, nodeName, src):
	particles = node.getElementsByTagName(nodeName)
	for particle in particles:
		try:
			particlefx = particle.childNodes[0].data
		except:
			showMsgFile(id, "particle tag have incorrect data", True)

		testParticle(id, particlefx, src)



def testSounds(id, node, type):
	global errors
	for sound in node.getElementsByTagName("sound"):
		try:
			event = sound.attributes["event"].value
		except:
			print "error: no sound event name in id=" + id
			errors = errors + 1

		if type == "monster":
			if event != "hit" and event != "miss" and event != "hurt" and event != "die" \
					and event != "move" and event != "sit" and event != "spawn":
				print "error: incorrect sound event name " + event + " in id=" + id
				errors = errors + 1
		elif type == "item":
			if event != "hit" and event != "strike":
				print "error: incorrect sound event name " + event + " in id=" + id
				errors = errors + 1

		testSound(sound.childNodes[0].data, sfxDir)

def testNpcs(file):
	global warnings, errors
	print "Checking npcs.xml"
	dom = minidom.parse(parentDir + file)
	idset = set()
	for node in dom.getElementsByTagName("npc"):
		try:
			id = node.attributes["id"].value
		except:
			print "error: no id for npc"
			errors = errors + 1
			continue
		
		if id in idset:
			print "error: duplicate npc id=" + id
		else:
			idset.add(id)

		testSprites(id, node, False, True, True, "", True)
		testParticles(id, node, "particlefx", file)

def readAttrI(node, attr, dv, msg, iserr):
	return int(readAttr(node, attr, dv, msg, iserr))

def readAttr(node, attr, dv, msg, iserr):
	global warnings, errors
	try:
		return node.attributes[attr].value
	except:
		print msg
		if iserr:
			errors = errors + 1
		else:
			warnings = warnings + 1
		return dv


def testMap(file, path):
	global warnings, errors
	fullPath = parentDir + "/" + path
	dom = minidom.parse(fullPath)
	root = dom.documentElement
	mapWidth = readAttrI(root, "width", 0, "error: missing map width: " + file, True)
	mapHeight = readAttrI(root, "height", 0, "error: missing map height: " + file, True)
	mapTileWidth = readAttrI(root, "tilewidth", 0, "error: missing tile width: " + file, True)
	mapTileHeight = readAttrI(root, "tileheight", 0, "error: missing tile height: " + file, True)
	if mapWidth == 0 or mapHeight == 0 or mapTileWidth == 0 or mapTileHeight == 0:
		return

	if mapWidth < borderSize * 2 + 1:
		showMsgFile(file, "map width to small: " + str(mapWidth), False)
	if mapHeight < borderSize * 2 + 1:
		showMsgFile(file, "map height to small: " + str(mapHeight), False)

	tilesMap = dict()

	for tileset in dom.getElementsByTagName("tileset"):
		try:
			source = tileset.attributes["source"].value
			if source is not None and source != "":
				file2 = os.path.abspath(parentDir + os.path.sep + mapsDir + source)
				if not os.path.isfile(file2):
					showMsgFile(file, "missing source file in tileset " + source, True)

				continue;
		except:
			None

		name = readAttr(tileset, "name", "", "warning: missing tile name: " + file, False)
		tileWidth = readAttrI(tileset, "tilewidth", mapTileWidth, \
				"error: missing tile width in tileset: " + name + ", " + file, True)
		tileHeight = readAttrI(tileset, "tileheight", mapTileHeight, \
				"error: missing tile height in tileset: " + name + ", " + file, True)
		try:
			firstGid = int(tileset.attributes["firstgid"].value)
		except:
			firstGid = 0

		if firstGid in tilesMap:
			showMsgFile(file, "tile with firstgid " + str(firstGid) + \
					" already exist: " + name + ", " + file, True)
			continue

		if tileWidth == 0 or tileHeight == 0:
			continue

		tile = Tileset()
		tile.name = name
		tile.width = tileWidth
		tile.tileWidth = tileWidth
		tile.height = tileHeight
		tile.tileHeight = tileHeight
		tile.firstGid = firstGid
		tile.lastGid = 0

#		if tileWidth != 32:
#			showMsgFile(file, "tile width " + str(tileWidth) + " != 32: " + name, False)
#		if tileHeight != 32:
#			showMsgFile(file, "tile height " + str(tileHeight) + " != 32: " + name, False)

		images = tileset.getElementsByTagName("image")
		if images == None or len(images) == 0:
			showMsgFile(file, "missing image tags in tile " + name, True)
			continue
		elif len(images) > 1:
			showMsgFile(file, "to many image tags in tile " + name, True)
			continue
		else:
			image = images[0]
			source = readAttr(image, "source", None, "error: missing source in image tag in tile " \
					+ name + ": " + file, True)
			if source != None:
				imagePath = os.path.abspath(parentDir + "/" + mapsDir + source)

				img = splitImage(imagePath)
				imagePath = img[0]
				imagecolor = img[1]

				tile.image = imagePath
				tile.color = imagecolor

				if not os.path.isfile(imagePath) or os.path.exists(imagePath) == False:
					showMsgFile(file, "image file not exist: " + mapsDir + source + ", " + \
							name, True)
					continue

				if imagecolor != "":
					testDye("", imagecolor, source, file, True)

				sz = testImageFile(file, imagePath, 0, "", True)
				width = sz[0]
				height = sz[1]

				if width == 0 or height == 0:
					continue
				
				if width < tileWidth:
					showMsgFile(file, "tile width more than image width in tile: " + \
							name, True)
					continue
				if height < tileHeight:
					showMsgFile(file, "tile height more than image height in tile: " + \
							name, True)
					continue

				s1 = int(width / int(tileWidth)) * int(tileWidth)

				if width != s1:
					if s1 == 0:
						s1 = int(tileWidth)
					showMsgFile(file, "image width " + str(width) + \
							" (need " + str(s1) + ") is not multiply to tile size " + \
							str(tileWidth) + ". " + source + ", " + name, False)

				s2 = int(height / int(tileHeight)) * int(tileHeight)

				tile.lastGid = tile.firstGid + (int(width / int(tileWidth)) * int(height / int(tileHeight))) - 1
				if height != s2:
					if s2 == 0:
						s2 = int(tileHeight)
					showMsgFile(file, "image width " + str(height) + \
							" (need " + str(s2) + ") is not multiply to tile size " + \
							str(tileHeight) + ". " + source + ", " + name, False)

		tilesMap[tile.firstGid] = tile
					

	testTiles(file, tilesMap)
	layers = dom.getElementsByTagName("layer")
	if layers == None or len(layers) == 0:
		showMsgFile(file, "map dont have layers", True)
		return

	fringe = None
	collision = None
	lowLayers = [] 
	overLayers = []
	beforeFringe = True

	for layer in layers:
		name = readAttr(layer, "name", None, "layer dont have name", True)
		if name == None:
			continue
		obj = Layer()
		obj.name = name
		if name.lower() == "fringe":
			if fringe is not None:
				showMsgFile(file, "duplicate Fringe layer", True)
			fringe = obj
			beforeFringe = False
		elif name.lower() == "collision":
			if collision is not None:
				showMsgFile(file, "duplicate Collision layer", True)
			collision = obj
		elif beforeFringe == True:
			lowLayers.append(obj)
		else:
			overLayers.append(obj)
			
		width = readAttrI(layer, "width", 0, "error: missing layer width: " + name + \
				", " + file, True)
		height = readAttrI(layer, "height", 0, "error: missing layer height: " + name + \
				", " + file, True)
		if width == 0 or height == 0:
			continue

		obj.width = width
		obj.height = height

		if mapWidth < width:
			showMsgFile(file, "layer width " + str(width) + " more than map width " + \
					str(mapWidth) + ": " + name, True)
		if mapHeight < height:
			showMsgFile(file, "layer height " + str(height) + " more then map height " + \
					str(mapHeight) + ": " + name, True)

		obj = testLayer(file, layer, name, width, height, obj, tilesMap)

	if fringe == None:
		showMsgFile(file, "missing fringe layer", True)
	if collision == None:
		showMsgFile(file, "missing collision layer", True)
	else:
		ids = testCollisionLayer(file, collision, tilesMap)
		if ids[0] != None and len(ids[0]) > 0:
			showLayerErrors(file, ids[0], "empty tiles in collision border", False)
		if ids[1] != None and len(ids[1]) > 0:
			showLayerErrors(file, ids[1], "incorrect tileset index in collision layer", False)

	if len(lowLayers) < 1:
		showMsgFile(file, "missing low layers", False)
	if len(overLayers) < 1:
		showMsgFile(file, "missing over layers", False)

	if fringe != None:
		lowLayers.append(fringe)
	warn1 = None

	if len(overLayers) > 0:
		testData = dict() 
		warn1 = testLayerGroups(file, lowLayers, collision, None, tilesMap, False)
		lowLayers.extend(overLayers)
		err1 = testLayerGroups(file, lowLayers, collision, testData, tilesMap, False)
		reportAboutTiles(file, testData)
	else:
		testData = dict()
		err1 = testLayerGroups(file, lowLayers, collision, testData, tilesMap, False)
		reportAboutTiles(file, testData)

	if warn1 != None and err1 != None:
		warn1 = warn1 - err1
	if warn1 != None and len(warn1) > 0:
		showLayerErrors(file, warn1, "empty tile in lower layers", False)
	if err1 != None and len(err1) > 0:
		showLayerErrors(file, err1, "empty tile in all layers", True)


def testTiles(file, tilesMap):
	for firstGid in tilesMap:
		for gid2 in tilesMap:
			if firstGid != gid2:
				tile1 = tilesMap[firstGid]
				tile2 = tilesMap[gid2]
				if (tile1.firstGid >= tile2.firstGid and tile1.firstGid <= tile2.lastGid) or \
					(tile1.lastGid >= tile2.firstGid and tile1.lastGid <= tile2.lastGid):
						showMsgFile(file, "overlaping tilesets gids \"" + tile1.name \
								+ "\" and \"" + tile2.name + "\"", True)




def reportAboutTiles(file, data):
	if testBadCollisions == False:
		return
	for k in data:
		d = data[k]
		if d[0] != 0 and d[2] != 0:
			#print file + ": " + str(k) + ": " + str(d)
			testCollisionPoints(file, k, d, 1, 3, \
				"possible tiles should be without collision: ", \
				"because no collision: ", False)
			testCollisionPoints(file, k, d, 3, 1, \
				"possible tiles should be with collision: ", \
				"because collision: ", False)


def testCollisionPoints(file, tileId, data, idx1, idx2, msg1, msg2, iserr):
	#print "test: " + str(idx1) + ", " + str(idx2)
	cnt1 = 0
	cnt2 = 0
	for point in data[idx1]:
		if point[2] > 0:
			cnt1 = cnt1 + 1
	for point in data[idx2]:
		if point[2] > 0:
			cnt2 = cnt2 + 1

	ln1 = len(data[idx1])
	ln2 = len(data[idx2])
	#print "cnt1=" + str(cnt1) + ", cnt2=" + str(cnt2) + ", ln1=" + str(ln1) + ", ln2=" + str(ln2)
	if ln1 > 0 and ln2 > 0 and cnt2 > 0 and cnt2 < cnt1 - tileNumDiff and cnt2 < maxNumErrTiles:
		text = msg1
		c = 0
		for point in data[idx2]:
			if point[2] > 0:
				if c > 100:
					break
				text = text + "(" + str(point[0]) + ", " + str(point[1]) + "), "
				c = c + 1
		text = text[:len(text)-2] + " " +  msg2
		c = 0
		for point in data[idx1]:
			if c > 100:
				break
			text = text + "(" + str(point[0]) + ", " + str(point[1]) + "), "
			c = c + 1
		showMsgFile(file, text[:len(text)-2], iserr)
	


def testCollisionLayer(file, layer, tiles):
	haveTiles = False
	tileset = set()
	badtiles = set()
	arr = layer.arr
	x1 = borderSize 
	y1 = borderSize
	x2 = layer.width - 20
	y2 = layer.width - 20
	if x2 < 0:
		x2 = 0
	if y2 < 0:
		y2 = 0

	if arr is None :
		return (set(), set())

	for x in range(0, layer.width):
		if haveTiles == True:
			break
		for y in range(0, layer.height):
			idx = ((y * layer.width) + x) * 4
			val = getLDV(arr, idx)
			if val != 0:
				haveTiles = True
				tile = findTileByGid(tiles, val)
				if tile is not None:
					idx = val -  tile.firstGid
					if idx > 1:
						badtiles.add(((x, y), idx))
			if val == 0 and (x < x1 or x > x2 or y < y1 or y > y2):
				tileset.add((x, y))

	
	if haveTiles == False:
		showMsgFile(file, "empty collision layer", False)
		return (set(), set())

	return (tileset, badtiles)


def findTileByGid(tiles, gid):
	for firstGid in tiles:
		if firstGid <= gid:
			tile = tiles[firstGid]
			if tile.lastGid >= gid:
				return tile
			
	return None


def showLayerErrors(file, points, msg, iserr):
	txt = ""
	cnt = 0
	for point in points:
		txt = txt + " " + str(point) + ","
		cnt = cnt + 1 
		if cnt > 100:
			txt = txt + " ... "
			break
	showMsgFile(file, msg + txt[0:len(txt)-1], iserr)


def getLDV(arr, index):
	return arr[index] | (arr[index + 1] << 8) | (arr[index + 2] << 16) \
		    | (arr[index + 3] << 24)


def getLDV2(arr, x, y, width, height, tilesMap):
	ptr = ((y * width) + x) * 4
	res = getLDV(arr, ptr)
	yend = height - 1
	if yend - y > 5:
		yend = y + 5
	for y2 in range(height - 1, y, -1):
		x0 = x - 3
		if x0 < 0:
			x0 = 0
		for x2 in range(x0, x + 1):
			ptr = ((y2 * width) + x2) * 4
			val = getLDV(arr, ptr)
			tile = findTileByGid(tilesMap, val)
			if tile is not None:
				if (tile.tileHeight > 32 or y2 == y) and (tile.tileWidth > 32 or x2 == x):
					hg = tile.tileHeight / 32
					wg = tile.tileWidth / 32
					if (y2 - y < hg or y2 == y) and (x2 - x < wg or x2 == x):
						res = val

	return res


def testLayer(file, node, name, width, height, layer, tiles):
	datas = node.getElementsByTagName("data")
	if datas == None or len(datas) == 0:
		showMsgFile(file, "missing data tag in layer: " + name, True)
		return
	layer.arr = None
	for data in datas:
		try:
			encoding = data.attributes["encoding"].value
		except:
			encoding = ""
		try:
			compression = data.attributes["compression"].value
		except:
			compression = ""
		if encoding == "base64":
			if compression != "gzip":
				if compression != "zlib":
					showMsgFile(file, "invalid compression " + compression + \
							" in layer: " + name, True)
					continue
				else:
					showMsgFile(file, "not supported compression by old clients " \
							+ compression + " in layer: " + name, False)
			binData = data.childNodes[0].data.strip()
			binData = binData.decode('base64')
			if compression == "gzip":
				dc = zlib.decompressobj(16 + zlib.MAX_WBITS)
			else:
				dc = zlib.decompressobj()
			layerData = dc.decompress(binData)
			arr = array.array("B")
			arr.fromstring(layerData)
			layer.arr = arr

			# here may be i should check is tiles correct or not, but i will trust to tiled
	return layer


def testLayerGroups(file, layers, collision, tileInfo, tilesMap, iserr):
	width = 0
	height = 0
	errset = set()
	for layer in layers:
		if layer.width > width:
			width = layer.width
		if layer.height > height:
			height = layer.height

	for x in range(0, width):
		for y in range(0, height):
			good = False
			lastTileId = 0
			for layer in layers:
				if layer.arr != None and x < layer.width \
						and y < layer.height:
					arr = layer.arr
					ptr = ((y * layer.width) + x) * 4
					if testBadCollisions == True:
						val = getLDV2(arr, x, y, layer.width, layer.height, tilesMap)
					else:
						val = 0
					val1 = getLDV(arr, ptr)
					if val1 != 0:
						good = True
						if val == val1 and testBadCollisions == True: 
							lastTileId = val
			if good == False:
				errset.add((x,y))
			elif testBadCollisions == True and collision != None and tileInfo != None:
				if lastTileId not in tileInfo:
					tileInfo[lastTileId] = [0, set(), 0, set()]
				ti = tileInfo[lastTileId]
				flg = getLDV(collision.arr, ((y * collision.width) + x) * 4)
				cnt = countCollisionsNear(collision, x, y)
				k = 0
				if flg > 0:
					if cnt[1] < cnt[0] and cnt[0] - cnt[1] > 5:
						k = 1
					ti[2] = ti[2] + 1
					ti[3].add((x, y, k))
				else:
					if cnt[0] > cnt[1] and cnt[0] - cnt[1] > 5:
						k = 1
					ti[0] = ti[0] + 1
					ti[1].add((x, y, k))

					
	return errset

def countCollisionsNear(layer, x, y):
	arr = layer.arr
	x1 = x - 1
	y1 = y - 1
	x2 = x + 1
	y2 = y + 1
	col = 0
	nor = 0

	if x1 < 0:
		x1 = 0
	if x2 >= layer.width:
		x2 = layer.width - 1
	if y1 < 0:
		y1 = 0
	if y2 >= layer.height:
		y2 = layer.height - 1

	for f in range(x1, x2 + 1):
		for d in range(y1, y2 + 1):
			if f != x or d != y:
				val = getLDV(arr, ((d * layer.width) + f) * 4)
				if val == 0:
					nor = nor + 1
				else:
					col = col + 1
	return (nor, col)


def testMaps(dir):
	global warnings, errors
	fullPath = parentDir + "/" + dir
	print "Checking maps"
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		print "error: maps dir not found: " + dir
		errors = errors + 1
		return

	for file in os.listdir(fullPath):
		if filtmaps.search(file):
			testMap(mapsDir + file, dir + file)

def testDefaultFiles():
	print "Checking defult files"
	testSound(attackSfxFile, sfxDir)
	testSprite("0", spriteErrorFile, 0, True, "", True)
	testParticle("0", particlesDir + levelUpEffectFile, "levelUpEffectFile")
	testParticle("0", particlesDir + portalEffectFile, "portalEffectFile")
	fullName = parentDir + "/" + wallpapersDir + wallpaperFile
	if not os.path.isdir(fullName) and os.path.exists(fullName):
		testImageFile(wallpapersDir + wallpaperFile, fullName, 0, "", False)


def testMinimapsDir():
	global errors, warnings

	print "Checking minimaps"
	fullPath = parentDir + "/" + minimapsDir
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		print "warn: minimaps dir not exist"
		warnings = warnings + 1
		return
	for file in os.listdir(fullPath):
		if filtimages.search(file):
			fullName = parentDir + "/" + minimapsDir + file
			testImageFile(minimapsDir + file, fullName, 0, "", True)


def testImagesDir(imagesDir, sz):
	global errors, warnings

	fullPath = parentDir + "/" + imagesDir
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		return
	for file in os.listdir(fullPath):
		file2 = fullPath + "/" + file
		if file[0] == ".":
			continue
		if not os.path.isfile(file2):
			testImagesDir(imagesDir + file + "/", sz)
		if filtimages.search(file):
			fullName = parentDir + "/" + imagesDir + file
			testImageFile(imagesDir + file, fullName, sz, "", True)


def testSpritesDir(dir):
	global errors, warnings, safeDye

	fullPath = parentDir + "/" + spritesDir + dir
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		return
	
	for file in os.listdir(fullPath):
		file2 = fullPath + "/" + file
		if file[0] == ".":
			continue
		if not os.path.isfile(file2):
			testSpritesDir(dir + file + "/")
		if filtimages.search(file):
			fullName = parentDir + "/" + spritesDir + dir + file
			testImageFile(spritesDir + dir, fullName, 0, spritesDir + dir + file, True)
		elif filtxmls.search(file):
			fullName = dir + file
			safeDye = True
			testSprite("0", dir + file, 0, True, "", True)
			safeDye = False



def testParticlesDir(dir):
	global errors, warnings, safeDye

	fullPath = parentDir + "/" + dir
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		return
	for file in os.listdir(fullPath):
		file2 = fullPath + "/" + file
		if file[0] == ".":
			continue
		if not os.path.isfile(file2):
			testParticlesDir(dir + file + "/")
		if filtimages.search(file):
			fullName = parentDir + "/" + dir + file
			testImageFile(dir + file, fullName, 0, "", True)
		elif filtxmls.search(file):
			fullName = dir + file
			safeDye = True
			testParticle("0", dir + file, "")
			safeDye = False


def testSoundsDir(dir, sfxDir):
	global errors, warnings

	fullPath = parentDir + "/" + sfxDir + dir
	if not os.path.isdir(fullPath) or not os.path.exists(fullPath):
		print "warn: directory " + sfxDir + " not exist"
		warnings = warnings + 1
		return
	for file in os.listdir(fullPath):
		file2 = fullPath + "/" + file
		if file[0] == ".":
			continue
		if not os.path.isfile(file2):
			testSoundsDir(dir + file + "/", sfxDir)
		elif filtogg.search(file):
			fullName = dir + file
			testSound(dir + file, sfxDir)


def testItemColors(fileName):
	global warnings, errors, safeDye, colorLists
	print "Checking itemcolors.xml"
	try:
		dom = minidom.parse(parentDir + fileName)
	except:
		return

	for node in dom.getElementsByTagName("list"):
		if node.parentNode != dom.documentElement:
			continue

		try:
			name = node.attributes["name"].value
		except:
			print "error: colors list dont have name"
			errors = errors + 1
			continue
		if name in colorsList:
			print "error: duplicate color list: " + name
			errors = errors + 1
			continue
		colorsList.add(name)
		colors = set()
		names = set()
		for colorNode in node.getElementsByTagName("color"):
			if colorNode.parentNode != node:
				continue
			try:
				id = colorNode.attributes["id"].value
			except:
				print "error: getting id in list: " + name
				errors = errors + 1
				continue
			try:
				colorName = colorNode.attributes["name"].value
			except:
				print "error: getting name in list: " + name
				errors = errors + 1
				continue
			try:
				colorDye = colorNode.attributes["value"].value
			except:
				print "error: getting color in list: " + name
				errors = errors + 1
			if id in colors:
				print "error: color with id " + str(id) + " already in list: " + name
				errors = errors + 1
			else:
				colors.add(id)
			if colorName in names:
				print "error: color with name \"" + colorName + "\" already in list: " + name
				errors = errors + 1
			else:
				names.add(colorName)
			testDyeColors(id, colorDye, colorDye, name, True)

def haveXml(dir):
	if not os.path.isdir(dir) or not os.path.exists(dir):
		return False
	for file in os.listdir(dir):
		if filt.search(file):
			return True
	return False
		

def detectClientData(dirs):
	global parentDir

	for dir in dirs:
		if haveXml(dir):
			print "Detected client data directory in: " + dir
			parentDir = dir
			return True
	
	print "Cant detect client data directory"
	exit(1)


showHeader()
print "Detecting clientdata dir"
detectClientData([".", "..", parentDir])
print "Checking xml file syntax"
enumDirs(parentDir)
loadPaths()
testDefaultFiles()
testItemColors("/itemcolors.xml")
testItems("/items.xml", iconsDir)
testMonsters("/monsters.xml")
testNpcs("/npcs.xml")
testMaps(mapsDir)
testMinimapsDir()
print "Checking images dir"
testImagesDir(wallpapersDir, 0)
print "Checking icons dir"
testImagesDir(iconsDir, 32)
print "Checking sprites dir"
testSpritesDir("")
print "Checking particles dir"
testParticlesDir(particlesDir)
print "Checking sfx dir"
testSoundsDir("", sfxDir)
print "Checking music dir"
testSoundsDir("", musicDir)
showFooter()
