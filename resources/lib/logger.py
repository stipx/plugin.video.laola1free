# -*- coding: utf-8 -*-

import xbmc

# LOGDEBUG = 0
# LOGNOTICE = 2
# LOGINFO = 1
# LOGWARNING = 3
# LOGERROR = 4
# LOGSEVERE = 5
# LOGFATAL = 6
# LOGNONE = 7

def info(message, *arguments):
	log(message, arguments, xbmc.LOGINFO)

def error(message, *arguments):
	log(message, arguments, xbmc.LOGERROR)

def notice(message, *arguments):
	log(message, arguments, xbmc.LOGNOTICE)

def debug(message, *arguments):
	log(message, arguments, xbmc.LOGDEBUG)
	# maybe write the debug log stuff also in a variable to be able to write
	# it when the exception gets handled in default.py or add a debug log setting to addon settings

def warn(message, *arguments):
	log(message, arguments, xbmc.LOGWARNING)

def log(message, arguments, level):
	xbmc.log(message.format(*arguments), level)