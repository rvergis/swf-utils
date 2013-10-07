swf-utils
=========

Command Line Utilities for files in SWF format


## is-swf-debug-enabled.py

Run this script on your SWF to check if the swf has debug enabled.

### Setup

1. You need Python. I've tested 2.7.4 (Mac)
1. For LZMA-compressed SWFs, you need [pylzma](http://www.joachim-bauch.de/projects/pylzma/).

### Usage

        ./is-swf-debug-enabled swf_file

Output text will indicate if SWF has debug enabled.