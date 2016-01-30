# -*- coding: utf-8 -*-

import urllib2
import string
import time
from urlparse import urljoin
from bs4 import BeautifulSoup

class Extractor:
	def __init__(self, baseurl):
		self.baseurl = baseurl
		
	def get_soup(self):
		source = urllib2.urlopen(self.baseurl)
		return BeautifulSoup(source)
		
	def get_text(self, item):
		return item.get_text().strip().encode('utf-8')
		
	def get_url(self, url):
		return urljoin(self.baseurl, url.encode('utf-8'))
		
	def determine_icon(self, s):
		if 'volley' in s or 'handball' in s:
			return 'resource:icons/volleyball.png'
		if 'football' in s:
			return 'resource:icons/soccer.png'
		if 'hockey' in s:
			return 'resource:icons/hockey.png'
		if 'basketball' in s:
			return 'resource:icons/basketball.png'
		if 'motorsports' in s:
			return 'resource:icons/motorsport.png'
		if 'tennis' in s:
			return 'resource:icons/tennis.png'
		if 'all' in s:
			return 'resource:icons/gymnastics.png'
		return 'DefaultFolder.png'
		
		
	def extract_channels(self, nodes):
		items = []
		for child in nodes:
			if child.span is not None and child.ul is not None:
				children = self.extract_channels(child.ul.find_all('li', recursive=False))
				if children:
					item = {
						'label': self.get_text(child.span),
						'children': children,
						'type': 'channel'
					}
					
					if child.span.i:
						item['image'] = self.determine_icon(' '.join(child.span.i['class']))
					
					items.append(item)
					continue

			if child.a is not None:
				link = child.a
				
				item = {
					'label': self.get_text(link),
					'url': self.get_url(link['href']),
					'type': 'channel'
				}
				
				if link.img:
					item['image'] = self.get_url(link.img['src'])
				
				items.append(item)

		return items
		
	def extract_live_block(self, parent):
		link = parent.select('.meta a.live')[0]
		
		return {
			'label': self.get_text(link.span) + ' ([COLOR red]' + self.get_text(link.i) + '[/COLOR])',
			'type': 'live-block',
			'url': self.get_url(link['href'])
		}
		
	def extract_blocks(self, parent):
		list = []
		for node in parent.select('.teaser-wrapper'):
			title = node.select('.teaser-title')[0]
			
			if title.a is not None:
				list.append({
					'label': self.get_text(title.a.h2),
					'url': self.get_url(title.a['href']),
					'image': self.get_url(node.select('.teaser-list .teaser img')[0]['src']),
					'type': 'block'
				})
				continue
				
			if title.h2 is not None:
				children = self.extract_videos(node)
					
				if children:
					list.append({
						'label': self.get_text(title.h2),
						'children': children,
						'image': self.get_url(node.select('.teaser-list .teaser img')[0]['src']),
						'type': 'block'
					})
					
		return list
		
	def extract_live_videos(self, parent):
		list = []
		for item in parent.select('.list-day .item'):
			h2s = item.select('.heading h2')
			if not h2s:
				continue
			
			datas = item.select('.badge a > span')
			
			if not datas:
				continue;
				
			data = datas[0]
			
			if int(data['data-sstatus'].encode('utf-8')) == 4:
				date = '[COLOR red]LIVE[/COLOR] - '
			else:
				# 2016-1-30-20-30-00
				date = data['data-nstreamstart'].encode('utf-8')
				datetime = time.strptime(date, '%Y-%m-%d-%H-%M-%S')
				date = '[B]' + time.strftime('%a, %H:%M', datetime) + '[/B] - '
				
			list.append({
				'label': date + self.get_text(h2s[0]),
				'url': self.get_url(item.select('a')[0]['href']),
				'image': self.get_url(item.select('.logo img')[0]['src']),
				'type': 'video'
			})
				
		return list
		
	def extract_next_page_link(self, parent):
		nexts = parent.select('.paging .next')
		if nexts and 0 < len(nexts):
			return {
				'label': 'More...',
				'url': self.get_url(nexts[0].find_parent('a')['href']),
				'type': 'block'
			}
			
		return None
		
	def extract_videos(self, parent):
		children = []
		for teaser in parent.select('.teaser-list .teaser a'):
			badge = teaser.select('.badge')[0]
			date = self.get_text(badge)
			
			if 'live' in badge['class']:
				# Fri 19.02.2016  19:10
				date = date[4:]
				datetime = time.strptime(date, '%d.%m.%Y  %H:%M')
				starttime = ' - [COLOR red]' + time.strftime('%H:%M', datetime) + '[/COLOR]'
			else:
				# 10.01.2016
				datetime = time.strptime(self.get_text(badge), '%d.%m.%Y')
				starttime = ''
			
			date = '[B]' + time.strftime('%a, %d.%m.%Y', datetime) + '[/B] - '
		
			children.append({
				'label': date + self.get_text(teaser.find('p', recursive=False)) + starttime,
				'url': self.get_url(teaser['href']),
				'image': self.get_url(teaser.select('img')[0]['src']),
				'type': 'video'
			})
				
		return children
	
	def get_channels(self):
		soup = self.get_soup()
		return [self.extract_live_block(soup)] + self.extract_channels(soup.select('.quick-browse .level1 > li'))
		
	def get_blocks(self):
		soup = self.get_soup()
		return self.extract_blocks(soup)
		
	def get_live_videos(self):
		soup = self.get_soup()
		return self.extract_live_videos(soup)
		
	def get_videos(self):
		soup = self.get_soup()
		videos = self.extract_videos(soup)
		next = self.extract_next_page_link(soup)
		if next:
			videos.append(next)
			
		return videos