# -*- coding: utf-8 -*-

import urllib2
import re
import string
import random
from urlparse import urljoin
from bs4 import BeautifulSoup

class StreamError(Exception):
	def __init__(self, message):
		self.message = message

class Stream:
	def __init__(self, url, min_bandwidth = 0, max_bandwidth = 999999999):
		self.min_bandwidth = min_bandwidth
		self.max_bandwidth = max_bandwidth
		
		url = self.get_videoplayer_url(url)
		url = self.get_details_url(url)
		self.url = self.get_playlist_url(url)
		
	def get_videoplayer_url(self, url):	
		source = urllib2.urlopen(url)
		soup = BeautifulSoup(source)
		
		# TODO some more info maybe?
		self.title = soup.select('title')[0].get_text().strip().encode('utf-8')

		iframes = soup.select('.videoplayer iframe')
		
		if len(iframes) == 0:
			raise StreamError(self.find_error_reason(soup))
		
		return urljoin(url, iframes[0]['src'])
		
	def find_error_reason(self, soup):
		countdown = soup.select('.videoplayer-overlay .countdown p')
		if countdown:
			return 'Stream not yet started![CR]Stream start: ' + countdown[0].get_text().strip().encode('utf-8')
			
		if not 'LAOLA1.tv' in self.title:
			return 'Stream not supported:[CR]' + self.title
			
		return 'Videoplayer not found!'
		
	def get_details_url(self, url):
		source = urllib2.urlopen(url)
		content = source.read()
		source.close()

		streamid = re.compile('streamid: "(.+?)"', re.DOTALL).findall(content)[0]
		partnerid = re.compile('partnerid: "(.+?)"', re.DOTALL).findall(content)[0]
		portalid = re.compile('portalid: "(.+?)"', re.DOTALL).findall(content)[0]
		sprache = re.compile('sprache: "(.+?)"', re.DOTALL).findall(content)[0]
		auth = re.compile('auth = "(.+?)"', re.DOTALL).findall(content)[0]
		timestamp = ''.join(re.compile('<!-- ([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}) -->', re.DOTALL).findall(content)[0])

		hdvideourl = 'http://www.laola1.tv/server/hd_video.php?play='+streamid+'&partner='+partnerid+'&portal='+portalid+'&v5ident=&lang='+sprache

		source = urllib2.urlopen(hdvideourl)
		soup = BeautifulSoup(source)

		return soup.videoplayer.url.text +'&timestamp='+timestamp+'&auth='+auth
		
	def char_gen(self, size=1, chars=string.ascii_uppercase):
		return ''.join(random.choice(chars) for x in range(size))
		
	def get_playlist_url(self, url):
		source = urllib2.urlopen(url)
		soup = BeautifulSoup(source)

		auth = soup.data.token['auth']
		url = soup.data.token['url']

		baseurl = url.replace('/z/', '/i/')
		return urljoin(baseurl, 'master.m3u8?hdnea=' + auth + '&g=' + self.char_gen(12) + '&hdcore=3.8.0')
		
	def get_title(self):
		return self.title
		
	def get_url(self):
		return self.url
		
	def get_playlist(self):
		streamurl = self.get_url()
		source = urllib2.urlopen(streamurl)
		master = source.read()
		source.close()
		
		playlist = '#EXTM3U\n'
		
		for header, bandwidth, url in re.compile('(BANDWIDTH=(.+?),.+?)\n(.+?)\n', re.DOTALL).findall(master):
			bandwidth = int(bandwidth)
			if self.min_bandwidth < bandwidth and bandwidth <= self.max_bandwidth:
				playlist += header + '\n' + urljoin(streamurl, url) + '\n'
		
		return playlist