# -*- coding: utf-8 -*-

from resources.lib.handlers import *
import resources.lib.logger
import urlparse

logger.info('Starting addon with {}', sys.argv)

addonhandle = int(sys.argv[1])
addonbaseurl = sys.argv[0]
parameters = urlparse.parse_qs(sys.argv[2][1:])
baseurl = 'http://www.laola1.tv/en-int/'

type = parameters.get('type', ['channel'])[0]

handler = None
if type == 'channel':
	handler = ChannelHandler(addonhandle, addonbaseurl, parameters, baseurl)
elif type == 'live-block':
	handler = LiveBlockHandler(addonhandle, addonbaseurl, parameters, baseurl)
elif type == 'block':
	handler = BlockHandler(addonhandle, addonbaseurl, parameters, baseurl)
elif type == 'video':
	handler = VideoHandler(addonhandle, addonbaseurl, parameters, baseurl)

handler.handle()
handler.finish()
