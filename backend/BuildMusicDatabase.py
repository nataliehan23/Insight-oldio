"""
# Build Music Basebase:
# 1) Select top 1000 Music Album from original musicinfo based on Number of ratings and average rating
     In following iterations, select the recommended musicBs from recommendation database. 
# 2) Scrape Amazon for album artist, if unknown, throw away album.
# 3) Filter album with duplicate titles with NLTK. 
# 4) Grab information from Google API for youtube link, from Bing API for image, from Wikipedia for album infomation.
# 5) Save album information into database with more information:
     create table musics (ID TEXT, Title TEXT, Author TEXT, ImgURL TEXT, YouTubeURL TEXT, Wiki TEXT);
# 6) Output is the CD Title in a file for search autocomplet
# 7) Output also the music infomation: Title, URL for website display. 

@author: nataliehan23
@time: Jan 24. Friday, 2014
"""

import MySQLdb
import json
from ScrapeMusicInfo import *
import os, sys
from utilities import *

## Select top 1000 Music Album from original musicdata based on Number of ratings and average rating
## These are the seed albums to start the building of database
def selectTop1KMusic():
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	cmd = """select MusicID, MusicTitle, avg(Rating) as avgR, MusicRatingNum as number
			from Musicinfo 
			group by MusicID 
			having avgR > 4.3 
			order by MusicRatingNum DESC,
			avgR DESC  
			limit 1000;"""
	cur.execute(cmd)
	CDs = cur.fetchall()
	# save into json file
	with open('topmusic1000.json', 'wb') as fp:
		json.dump(CDs,fp)
	return CDs

## This function will load the topmusic1K data, find artists from Amazon API
## remove album with unknown artists, remove album with duplicate titles with NLTK
def removeDuplicateTitles(CDs):
	CDID = [cd[0] for cd in CDs]
	CDTitle = [cd[1] for cd in CDs]
	Rating = [cd[2] for cd in CDs]
	NewCDID = []
	NewCDTitle = []
	titles = []
	# remove ending () or []
	for i in range(len(CDs)):
		print "remove duplicate title:", i
		if Rating[i] <= 5:
			title = CDTitle[i]
			title = title.split()
			if '(' in title[-1] or '[' in title[-1]:
				title = " ".join(title[:-1])
			else:
				title = " ".join(title)
			if not inCommonSet(title.lower(), titles):
				titles.append(title.lower())
				NewCDTitle.append(title)
				NewCDID.append(CDID[i])
	print "saving results after removing duplicate titles..."
	Results = []
	for cdid, cdtitle in zip(NewCDID, NewCDTitle):
		Results.append([cdid,cdtitle])
	with open('/Users/natalie/Insight/myapp/djcloud/backend/json/removeduplicatetitle1k.json','wb') as fp:
		json.dump(Results,fp)
	return NewCDID, NewCDTitle

# find all the albums with unknown artists, remove them
def removeUnknownArtists(CDIDs, CDTitles):
	NewIDs = []
	NewTitles = []
	NewAuthors = []
	for i in range(len(CDIDs)):
		print "remove unknown artists:", i
		author = findAuthor(CDIDs[i])
		if author == 'unknown':
			print "author is unknow"
			# author = findAuthorAMZ(CDIDs[i])
			# if author == 'unknown':
			# 	pass
			# else:
			# 	print "author: ", author, "title: ", CDTitles[i]
			# 	NewAuthors.append(author)
			# 	NewIDs.append(CDIDs[i])
			# 	NewTitles.append(CDTitles[i])
		else:
			print "author: ", author, "title: ", CDTitles[i]
			NewAuthors.append(author)
			NewIDs.append(CDIDs[i])
			NewTitles.append(CDTitles[i])

	print "saving results after removing unknown artists..."
	Results = []
	for cdid, cdtitle, cdauthor in zip(NewIDs, NewTitles, NewAuthors):
		Results.append([cdid,cdtitle, cdauthor])
	with open('/Users/natalie/Insight/myapp/djcloud/backend/json/removeunknownartist1k.json','wb') as fp:
		json.dump(Results,fp)
	return NewIDs, NewTitles, NewAuthors

# find more music information, youtube link, image URL, Wiki Snip, save into musics database
def SaveToMusicsDatabase(NewIDs, NewTitles, NewAuthors):
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	ImgURLs = []
	WikiSnips = []
	YoutubeURLs = []
	for i in range(len(NewIDs)):
		print "Saving into database...", i
		cdid = NewIDs[i]
		print "Album ID is:", cdid
		title = NewTitles[i]
		print "Album title is: ", title
		author = NewAuthors[i]
		print "Album author is: ", author
		YoutubeURL = youtubeLinkGoogle(author, title)
		print "Youtube URL is", YoutubeURL
		ImgURL = imageLinkBing(author, title)
		print "Image URL is", ImgURL
		WikiSnips = findSnipWiki(title)
		WikiSnips = WikiSnips.replace('"','').replace("'","") + '!'
		WikiSnips = (WikiSnips[:500] + '!') if len(WikiSnips) > 500 else WikiSnips
		print "Wiki is:", WikiSnips
		print "MySQL command is:"
		# store into database
		dbcmd = '''INSERT INTO musics (ID, Title, Author, ImgURL, YouTubeURL, Wiki) VALUES ("'''
		dbcmd = dbcmd + cdid + '''" ,"''' + title + '''" ,"''' + author + '''" ,"'''
		try:
			dbcmd = dbcmd + ImgURL + '''" ,"''' + YoutubeURL + '''" ,"''' + WikiSnips.encode('utf-8') + '''");'''
		except:
			print "mysql command erro"
			continue
		print dbcmd
		try:
			cur.execute(dbcmd)
		except:
			print "insert error!"
			continue
		db.commit()
	return


# retrive CD Title and ImgURL from musics database for website
def retrieveFromDB():
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	# cmd = "select MusicTitle, ImgLink from music;"
	cmd = "select Title, ImgURL from musics;"
	cur.execute(cmd)
	CDs = cur.fetchall()
	CDTitle = []
	ImgURL = []
	for cd in CDs:
		CDTitle.append(cd[0])
		ImgURL.append(cd[1])
	return CDTitle, ImgURL


# process the query results, find the top 500 CD with links to image url
def saveMusicTitleForAutoComplete(CDTitle, filename):
	with open(filename, 'wb') as fp:
		json.dump(CDTitle,fp)

def saveMusicImages(CDTitle, ImageURL, filename):
	dictRes = []
	for title, img in zip(CDTitle, ImageURL):
		dictRes.append([title,img])
	with open(filename,'wb') as fp:
		json.dump(dictRes,fp)


def main():
	# print "Select top musics...."
	# PopCDs = selectTopMusic()
	# json_data=open('/Users/natalie/Insight/myapp/djcloud/backend/json/topmusic1000.json')
	# CDs = json.load(json_data)
	# print "Total music: ", len(CDs)
	# print "Remove Duplicate Titles..."
	# NewCDID, NewCDTitle = removeDuplicateTitles(CDs)
	# print "Left music: ", len(NewCDID)
	# print "Removing unknown authors"
	# json_data=open('/Users/natalie/Insight/myapp/djcloud/backend/json/removeduplicatetitle1k.json')
	# CDs = json.load(json_data)
	# NewCDID=[]
	# NewCDTitle=[]
	# for i in range(len(CDs)):
	# 	NewCDID.append(CDs[i][0])
	# 	NewCDTitle.append(CDs[i][1])

	# NewIDs, NewTitles, NewAuthors = removeUnknownArtists(NewCDID, NewCDTitle)

	# print "Left music: ", len(NewIDs)
	json_data = open('/Users/natalie/Insight/myapp/djcloud/backend/json/removeunknownartist1k_me.json')
	CDs = json.load(json_data)
	NewIDs = []
	NewTitles = []
	NewAuthors = []
	for i in range(8,len(CDs)):
		NewIDs.append(CDs[i][0])
		NewTitles.append(CDs[i][1])
		NewAuthors.append(CDs[i][2])
	print "Saving music information into database..."
	SaveToMusicsDatabase(NewIDs, NewTitles, NewAuthors)
	outputdir = '/Users/natalie/Insight/myapp/djcloud/static/json'
	titlefile = 'AlbumTitles.json'
	imagefile = 'AlbumImages.json'
	CDTitle, ImgURL = retrieveFromDB()
	titlename = os.path.join(outputdir, titlefile)
	imagename = os.path.join(outputdir, imagefile)
	saveMusicTitleForAutoComplete(CDTitle,titlename)
	saveMusicImages(CDTitle, ImgURL, imagename)


if __name__ == '__main__':
	main()
