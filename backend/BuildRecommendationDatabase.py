"""
# Build Recommendation Basebase:
# 1) For each musicA from music database, and select the recommendation candidates musicBs(top 30 albums).
     Based on number of reviews
# 2) Merge data from Amazon API for album artist
# 3) Remove albums with the same title as musicA title with NLTK, keep only maximum two albums by the same author 
# 4) Keep final 5 albums, save musicB IDs to recommendation database.
     recommendation (musicA, musicB, similarty)
# 5) Find more information for recommended albums from Google API for youtube link, from Bing API for image, from Wikipedia for album infomation.
# 6) Save album information into music database with more information:
#    music (ID, Title, Author, Rating, ImgURL, YoutubeURL, WikiSnip)

@author: nataliehan23
@time: Jan 24. Friday, 2014
"""

import MySQLdb
import json
from ScrapeMusicInfo import *
from utilities import *
import os, sys



# retrive ID, Title and Author from music database
def findAllMusics():
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	# cmd = "select MusicTitle, ImgLink from music;"
	cmd = "select ID, Title, Author from musics;"
	cur.execute(cmd)
	CDs = cur.fetchall()
	CDIDs = []
	CDTitles = []
	Authors = []
	for cd in CDs:
		CDIDs.append(cd[0])
		CDTitles.append(cd[1])
		Authors.append(cd[2])
	return CDIDs, CDTitles, Authors


# find a particular music title based on it's id
def findMusicTitle(id):
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	query = '''SELECT MusicTitle from musicinfo where MusicID = ''' + "'" +id + '''';'''
	cur.execute(query)
	cdid = cur.fetchall()
	return cdid[0][0]

# For all musicID, select top similar CDs from the similarity database
# Filter top 6 selected CDs, grab more infomation(youtubelink, imagelink, snip)
# and save top 6 into a smaller database for recommendation
#   create table recommends(MusicAID TEXT, MusicATitle TEXT, MusicAAuthor TEXT, 
# 	MusicBID TEXT, MusicBTitle TEXT, MusicBAuthor TEXT, 
# 	Similarity FLOAT, ImgURL TEXT, YouTubeURL TEXT, Wiki TEXT);

def RecommendedCDs(CDIDs, CDTitles, Authors):
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	for i in range(len(CDIDs)):
		print "processing: ", i
		musicIDA = CDIDs[i]
		print "MusicA ID is: ", musicIDA
		# find out the title for musicA
		titleA = findMusicTitle(musicIDA)
		print "MusicA title is:", titleA
		# authorA = findAuthorAMZ(musicIDA)
		# print "MusicA author is: ", authorA

		# Query to find similar musci to recommend 
		query = '''SELECT MusicB, sim1, sim2, Num FROM Similarity WHERE MusicA = ''' + "'" + musicIDA + "'"
		query =  query + ''' AND sim1 >= 0.2 AND Num < 100 ORDER BY Num DESC, (sim1+sim2) DESC LIMIT 30;'''
		print query
		cur.execute(query)
		results = cur.fetchall()
		# filter 5 top albums with at most one same author as musicA, different titles. 
		TitleSet = []
		AuthorSet =[]
		TitleSet.append(titleA.lower())
		while len(TitleSet) < 6:
			for res in results:
				musicIDB = res[0]
				print "find music title"
				musicTitleB = findMusicTitle(musicIDB)
				print musicTitleB
				if not inCommonSet(musicTitleB.lower(), TitleSet):
					print "find music author"
					musicAuthorB = str(findAuthorAMZ(musicIDB))
					print musicAuthorB
					if musicAuthorB == "unknown" or (not inCommonSet(musicAuthorB.lower(), AuthorSet)):
						print "Add Author B", musicAuthorB," to authors list",  AuthorSet
						AuthorSet.append(musicAuthorB.lower())
						print "Add Title B", musicTitleB, "to title list",  TitleSet
						TitleSet.append(musicTitleB.lower())
						YoutubeURL = youtubeLinkGoogle(musicAuthorB, musicTitleB)
						print "Youtube URL is", YoutubeURL
						ImgURL = imageLinkBing(musicAuthorB, musicTitleB)
						print "Image URL is", ImgURL
						WikiSnips = findSnipWiki(musicTitleB)
						WikiSnips = WikiSnips.replace('"','').replace("'","") + '!'
						WikiSnips = (WikiSnips[:500] + '!') if len(WikiSnips) > 500 else WikiSnips
						print "Wiki is:", WikiSnips
						## save results into databas
						similarity = (res[1] +  res[2])/2
						dbcmd = '''INSERT INTO recommends (MusicAID, MusicATitle, MusicBID, MusicBTitle,'''
						dbcmd = dbcmd + '''MusicBAuthor, Similarity, ImgURL, YouTubeURL, Wiki) VALUES ("'''
						dbcmd = dbcmd + musicIDA + '''" ,"''' + titleA + '''" ,"''' + musicIDB + '''" ,"'''
						dbcmd = dbcmd + musicTitleB + '''" ,"''' + musicAuthorB + '''" ,"''' + str(similarity) + '''" ,"'''
						try:
							dbcmd = dbcmd + ImgURL + '''" ,"''' + YoutubeURL + '''" ,"''' + WikiSnips.encode('utf-8') + '''");'''
						except:
							print dbcmd
							print "coding error"
							continue
						print "MySQL command is:", dbcmd
						try:
							cur.execute(dbcmd)
						except:
							print "cannot insert into recommends"
							continue
						db.commit()
	return


def main():
	print "finding all music in musics database...."
	CDIDs, CDTitles, Authors = findAllMusics()
	print "total record: ", len(CDIDs)
	print "Build database for recommendation..."
	RecommendedCDs(CDIDs[3:], CDTitles[3:], Authors[3:])


if __name__ == '__main__':
	main()
