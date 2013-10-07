#!/usr/bin/env python
# Copyright (c) 2012, Adobe Systems Incorporated
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the 
# documentation and/or other materials provided with the distribution.
# 
# * Neither the name of Adobe Systems Incorporated nor the names of its 
# contributors may be used to endorse or promote products derived from 
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''See readme or run with no args for usage'''

import os
import sys
import tempfile
import shutil
import struct
import zlib
import hashlib
import inspect

supportsLZMA = False
try:
	import pylzma
	supportsLZMA = True
except:
	pass

####################################
# Helpers
####################################

class stringFile(object):
	def __init__(self, data):
		self.data = data

	def read(self, num=-1):
		result = self.data[:num]
		self.data = self.data[num:]
		return result

	def close(self):
		self.data = None

	def flush(self):
		pass

def consumeSwfTag(f):
	tagBytes = b""

	recordHeaderRaw = f.read(2)
	tagBytes += recordHeaderRaw
	
	if recordHeaderRaw == "":
		raise Exception("Bad SWF: Unexpected end of file")
	recordHeader = struct.unpack("BB", recordHeaderRaw)
	tagCode = ((recordHeader[1] & 0xff) << 8) | (recordHeader[0] & 0xff)
	tagType = (tagCode >> 6)
	tagLength = tagCode & 0x3f
	if tagLength == 0x3f:
		ll = f.read(4)
		longlength = struct.unpack("BBBB", ll)
		tagLength = ((longlength[3]&0xff) << 24) | ((longlength[2]&0xff) << 16) | ((longlength[1]&0xff) << 8) | (longlength[0]&0xff)
		tagBytes += ll
	tagBytes += f.read(tagLength)
	return (tagType, tagBytes)

####################################
# main()
####################################

if __name__ == "__main__":

	####################################
	# Parse command line
	####################################

	if len(sys.argv) < 1:
		print("Usage: %s SWF_FILE" % os.path.basename(inspect.getfile(inspect.currentframe())))
		sys.exit(-1)

	infile = sys.argv[1]

	####################################
	# Process SWF header
	####################################

	isDebug = False

	swfFH = open(infile, 'rb')
	signature = swfFH.read(3)
	swfVersion = swfFH.read(1)
	struct.unpack("<I", swfFH.read(4))[0] # uncompressed length of file

	if signature == b"FWS":
		pass
	elif signature == b"CWS":
		decompressedFH = stringFile(zlib.decompressobj().decompress(swfFH.read()))
		swfFH.close()
		swfFH = decompressedFH
	elif signature == b"ZWS":
		if not supportsLZMA:
			raise Exception("You need the PyLZMA package to use this script on \
				LZMA-compressed SWFs. http://www.joachim-bauch.de/projects/pylzma/")
		swfFH.read(4) # compressed length
		decompressedFH = stringFile(pylzma.decompress(swfFH.read()))
		swfFH.close()
		swfFH = decompressedFH
	else:
		raise Exception("Bad SWF: Unrecognized signature: %s" % signature)

	f = swfFH

	# FrameSize - this is nasty to read because its size can vary
	rs = f.read(1)
	r = struct.unpack("B", rs)
	rbits = (r[0] & 0xff) >> 3
	rrbytes = (7 + (rbits*4) - 3) / 8;
	f.read((int)(rrbytes))
	f.read(4) # FrameRate and FrameCount

	####################################
	# Process each SWF tag
	####################################

	while True:
		(tagType, tagBytes) = consumeSwfTag(f)
		if tagType == 0:
			break
		if tagType == 58: #EnableDebugger
			isDebug = True
		elif tagType == 64: #EnableDebugger2
			isDebug = True		
	
	####################################
	# Finish up
	####################################
	
	if isDebug:
		print("swftype is DEBUG ENABLED")
	else:
		print("swf is NOT DEBUG ENABLED")
