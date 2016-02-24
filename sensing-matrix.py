#!/usr/bin/env python

'''
Kim Ngo
Professor Dong Wang
CSE40437 - Social Sensing
24 February 2016

Generates sensing matrix file from twitter dataset and clustering results file
- twitter dataset format: json
- clustering results format: cluster#:tweet_id,tweet_id,...
- sensing matrix format: source_id,measured_variable_id (user_id,cluster_id of user's tweet)

Usage: ./sensing-matrix.py [twitter dataset] [clustering results file] [output file]
'''

import sys, json

def loadJsonTwitter(filename):
	tweets = {} # user_id:[twitter_ids]
 	with open(filename, 'r') as f:
		for line in f:
			tweet = json.loads(line)
			if tweet['from_user_id'] not in tweets:
				tweets[tweet['from_user_id']] = []
			tweets[tweet['from_user_id']].append(int(tweet['id']))
	return tweets

def loadClusterResults(filename):
	clusters = {} # tweet_id:cluster_id
	with open(filename, 'r') as f:
		for line in f:
			cluster_id, tweet_ids = line.strip().split(':')
			for tweet_id in tweet_ids.split(','):
				clusters[int(tweet_id)] = int(cluster_id)
	return clusters

def sensinMatrixDump(tweets, clusters, filename):
	# tweets dict: tweet
	# clusters dict: tweet_id:cluster_id
	f = open(filename, 'w')
	for user_id in tweets:
		measured_variables = []
		for tweet_id in tweets[user_id]:
			measured_variables.append(clusters[tweet_id])
		measured_variables.sort()
		for cluster in measured_variables:
			data = str(user_id) + ',' + str(cluster) + '\n'
			f.write(data)
	f.close()

def main():
	if len(sys.argv) != 4:
		print >> sys.stderr, 'Usage: %s [twitter dataset] [clustering results file] [output file]' % (sys.argv[0])
		sys.exit(-1)

	tweets = loadJsonTwitter(sys.argv[1])
	clusters = loadClusterResults(sys.argv[2])
	sensinMatrixDump(tweets, clusters, sys.argv[3])

if __name__ == '__main__':
	main()

