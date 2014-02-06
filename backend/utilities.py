import MySQLdb
import json
import os, sys
import nltk
import random
import string

# check if title is in a set, with natural language processing
def inCommonSet(title, titles):
	# print "checking common set"
	# print "Title: ", title
	# print "Title set: ", titles
	for i in range(len(titles)):
		if isCommonTitle(title, titles[i]):
			# print "finding in title set, return true"
			return True
	return False


## using Natural Language processing to determine common title
def isCommonTitle(titleA, titleB):
	# print "titleA: ", titleA
	# print "titleB: ", titleB
	titleA = titleA.split()
	if '(' in titleA[-1] or '[' in titleA[-1]:
		titleA = " ".join(titleA[:-1])
	else:
		titleA = " ".join(titleA)
	titleB = titleB.split()
	if '(' in titleB[-1] or '[' in titleB[-1]:
		titleB = " ".join(titleB[:-1])
	else:
		titleB = " ".join(titleB)

	tokensA = nltk.word_tokenize(titleA)
	tokensB = nltk.word_tokenize(titleB)
	ComTitle = list(set(tokensA).intersection(tokensB))
	if min(len(tokensA), len(tokensB)) > 4:
		if len(ComTitle) >=2:
			return True
		else:
			return False
	else:
		if len(ComTitle) >= 1:
			return True
		else:
			return False


# find a particular music title based on it's id
def findMusicTitle(id):
	db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")
	cur = db.cursor()
	query = '''SELECT MusicTitle from musicinfo where MusicID = ''' + "'" +id + '''';'''
	cur.execute(query)
	cdid = cur.fetchall()
	return cdid[0][0]


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

