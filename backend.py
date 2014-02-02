import sys
import MySQLdb
from pattern.web import Wikipedia, plaintext, Google
from pattern.web import Bing, IMAGE, Yahoo
from pattern import web
from scrapMusic import *


def recommender(title):
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	query = '''SELECT MusicAID, MusicATitle, MusicBID, MusicBTitle, MusicBAuthor,'''
	query = query + '''Pearson, Cosine, Num, ImageURL FROM recommender_s '''
	query = query + '''WHERE MusicATitle like "%''' + title + '''%" Limit 5;'''
	print query
	cur.execute(query)
	results = cur.fetchall()
	musics =[]
	i = 0
	for result in results:
		music = []
		music.append(result[2]) #musicid
		music.append(result[3]) #musictitle
		music.append(result[4]) #author
		music.append(result[5]) # pearson
		music.append(result[6]) # cosine
		music.append(result[7]) # Num
		music.append(result[8])
		youtubeurl = "//www.youtube.com/embed/Fi1sBwV1-tU"
		# youtubeurl = youtubeLink(result[4], result[3])
		# print youtubeurl
		# youtubeid = youtubeurl[youtubeurl.find('=')+1:]
		# youtubeurl = "//www.youtube.com/embed/" + youtubeid
		music.append(youtubeurl)
		music.append('This is a text')
		musics.append(music)
	return musics

def main():
	recommended = recommender(sys.argv[1])
	print recommended

if __name__ == '__main__':
	main()