from pattern.web import Wikipedia, plaintext, Google
from pattern.web import Bing, IMAGE, Yahoo
from pattern import web
import requests
import amazonproduct
from lxml import etree
import time
import random

# does not work much 
def findAuthor(asin):
	url = "http://www.amazon.com/dp/" + str(asin)
	r = requests.get(url)
	author = web.Element(r.text).by_class('buying')[0].by_tag('a')[0].content
	if author == "Amazon Prime":
		author = "unknown"
	return author

def findAuthorAMZ(asin):
	config = {
	'access_key': 'AKIAJ4LERDJC6GN22YPA',
	'secret_key': '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',
	'associate_tag': 'cloudrater-20',
	'locale': 'us'
	}
	api = amazonproduct.API(cfg=config)
	item = api.item_lookup(asin)
	itematt = item.Items.Item.ItemAttributes
	if hasattr(itematt, 'Artist'):
		author = itematt.Artist
	elif hasattr(itematt, 'Author'):
		author = itematt.Author
	else:
		author = 'unknown'
	time.sleep(5+random.randint(0,5))
	return author

def youtubeLink(author, album):
	if author == 'unknown':
		author = ''
	name = author + ' ' + album
	search = Google().search(name + " youtube")
	time.sleep(5+random.randint(0,5))
	return search[0].url

def youtubeLinkGoogle(author, album):
	if author == 'unknown':
		author = ''
	name = author + ' ' + album
	key='AIzaSyC0go1dbuPHJhGYnONXvBc8z9Q8GkBSosw'
	engine = Google(license=key, throttle=0)
	results = engine.search(name + " youtube")
	return results[0].url



def imageLinkBing(author, album):
	if author == 'unknown':
		author = ''
	name = author + ' ' + album
	result = Bing().search(name + " music album", type=IMAGE)
	time.sleep(5+random.randint(0,5))
	return result[0].url

def findSnip(author, album):
	if author == 'unknown':
		author = ''
	name = author + ' ' + album + ' album'
	search = Google().search(name)
	snip = plaintext(search[0].text)
	return snip 

def imageLinkAmazon(asin):
	url = "http://www.amazon.com/dp/" + str(asin)
	r = requests.get(url)
	iddiv = web.Element(r.text).by_id('main-image')
	target = iddiv.attr['src']
	print target
	return target



def findSnipWiki(album):
	result = Wikipedia().search(album)
	try:
		wiki = result.sections[0].content
	except:
		wiki = "I cannot find information from wikipedia about this album"
	Wiki = Wiki.replace('"','').replace("'","") + '!'
	Wiki = (Wiki[:500] + '!') if len(Wiki) > 500 else Wiki
	return wiki





