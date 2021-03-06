__author__ = 'juan'

import sqlite3 as lite
import json
from termcolor import colored
import mysql.connector

config = {
    'user': 'elec',
    'password': 'elec',
    'host': 'thor.deusto.es',
    'database': 'eu_test2',
}

class database:
    def __init__(self, db):
        self.db = db
        self.groups = []
        self.groups_ids = {}
        self.countries = {}
        self.parties = []
        self.locations = []
        self.con = mysql.connector.connect(**config)
        #self.groups = self.load_groups()
        #self.countries = self.load_countries()
        #self.parties = self.load_parties()
        #self.locations = self.load_locations()


    def create(self):
        try:
            with self.con:
                cursor = self.con.cursor()
                comm = "CREATE TABLE users (id INT, id_str TEXT, screen_name TEXT, total_tweets INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE tweets (id INT, user_id INT, id_str  TEXT ,text  TEXT, created_at  DATE, lang  TEXT, retweeted  BOOL);"
                cursor.execute(comm)
                comm = "CREATE TABLE interactions (user_id INT, target_id INT, day DATE, weight INT, mentions INT, retweets INT, replies INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE language_group (lang TEXT, group_id TEXT, total INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE language_candidate (lang TEXT, candidate_id INT, total INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE hash_country (text TEXT, country_id TEXT, day DATE, total INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE hash_group (text TEXT, group_id TEXT, day DATE, total INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE hash_candidate (text TEXT, candidate_id INT, day DATE, total INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE parties (initials TEXT, location_id TEXT, group_id TEXT, name TEXT, is_group_party BOOL, user_id INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE groups (candidate_id INT, initials TEXT, subcandidate_id INT, name TEXT, total_tweets INT, user_id INT);"
                cursor.execute(comm)
                comm = "CREATE TABLE locations (city TEXT, lat INT, lon INT, country_id TEXT);"
                cursor.execute(comm)
                comm = "CREATE TABLE countries (short_name TEXT, long_name TEXT, total INT);"
                cursor.execute(comm)

        except Exception, e:
             print "DB Error", e

    def insert(self,tweet):
        try:
            self.con = mysql.connector.connect(**config)
            tweet = json.loads(tweet)
            self.insert_users(tweet)
            #self.insert_tweets(tweet)
            #self.insert_reply(tweet)
            #self.insert_mentions(tweet)
            #self.insert_retweet(tweet)
            #self.insert_language_group(tweet)
            #self.insert_language_candidate(tweet)
            #self.insert_hash_country(tweet)
            #self.insert_hash_group(tweet)
            #self.insert_hash_candidate(tweet)
            self.con.commit()
            self.con.close()
        except Exception, e:
            print colored("Insertion error "+ e.message, "red")
            print tweet
            print "__________"

    def load_groups(self):
         try:
            with self.con:
                cursor = self.con.cursor()
                val =  cursor.execute("SELECT * from groups" ).fetchall()
                for v in val:
                    if v[0]:
                        self.groups_ids[v[0]] = v[1]
                    if v[2]:
                        self.groups_ids[v[2]] = v[1]
                    if v[5]:
                        self.groups_ids[v[5]] = v[1]
                return val
         except Exception, e:
             print "DB Error - load_groups ", e


    def load_countries(self):
         try:
            with self.con:
                cursor = self.con.cursor()
                val = cursor.execute("SELECT * from countries" ).fetchall()
            return val
         except Exception, e:
             print "DB Error - load_countries ", e


    def load_parties(self):
         try:
            with self.con:
                cursor = self.con.cursor()
                return cursor.execute("SELECT * from parties" ).fetchall()
         except Exception, e:
             print "DB Error - load_groups ", e

    def load_locations(self):
         try:
            with self.con:
                cursor = self.con.cursor()
                return cursor.execute("SELECT * from locations" ).fetchall()
         except Exception, e:
             print "DB Error - load_groups ", e

    def insert_users(self,tweet):
        #id INT, id_str TEXT, screen_name TEXT, total_tweets INT
        keys = [tweet['user']['id'], tweet['user']['id_str'], tweet['user']['screen_name'],1]
        print tweet['user']['id']
        try:
            cursor = self.con.cursor()
            select = "SELECT id, total_tweets from users where id="+str(keys[0])
            cursor.execute(select)
            node = cursor.fetchone()
            if node:
                print node
                total = node[1]+1
                update = "UPDATE users set total_tweets = "+str(total)+" where id = "+str(keys[0])
                cursor.execute(update)
            else:

                insert = "INSERT INTO users(id, id_str, screen_name, total_tweets) VALUES (" + str(keys[0]) + ",'" + keys[1] +"' ,'" + keys[2] + "', 1)"
                print insert
                cursor.execute(insert)


        except Exception, e:
            print "DB Error - insert_user: ", e



    def insert_tweets(self,tweet):
        # id INT, user_id INT, id_str  TEXT ,text  TEXT, created_at  DATE, lang  TEXT, retweeted  BOOL
        keys = [tweet['id'], tweet['user']['id'], tweet['user']['id_str'], tweet['text'], tweet['created_at'][:len(tweet['created_at'])-20], tweet['lang'], tweet['retweeted']]
        try:
            with self.con:
                cursor = self.con.cursor()
                cursor.execute("INSERT INTO tweets VALUES (?,?,?,?,?,?,?)",keys)
                if self.groups_ids.get(tweet['user']['id']):
                    cursor.execute("SELECT total_tweets FROM groups where initials = '"+str(self.groups_ids.get(tweet['user']['id']))+"'")
                    node = cursor.fetchone()
                    node[0] += 1
                    cursor.execute("UPDATE groups set total_tweets = "+str(node[0])+" where initials = '"+str(self.groups_ids.get(tweet['user']['id']))+"'")
        except Exception, e:
            print "DB Error - insert_tweet: ", e

    def insert_reply(self,tweet):
        #user_id INT, target_id INT, day DATE, weight INT, mentions INT, retweets INT, replies INT
        replies = tweet['in_reply_to_user_id']
        if replies:
            keys = [tweet['id'], replies, tweet['created_at'][:len(tweet['created_at'])-20], 1, 0, 0, 1]
            try:
                with self.con:
                    cursor = self.con.cursor()
                    cursor.execute("SELECT * from interactions where (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(replies)+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    node = cursor.fetchone()
                    if node:
                        total = node[3]+1
                        partial = node[6]+1
                        cursor.execute("UPDATE interactions set weight = "+str(total)+" ,replies = "+str(partial)+" WHERE (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(replies)+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    else:
                        cursor.execute("INSERT INTO interactions VALUES (?,?,?,?,?,?,?)",keys)
            except Exception, e:
                print "DB Error - insert_reply: ", e

    def insert_mentions(self,tweet):
        #user_id INT, target_id INT, day DATE, weight INT, mentions INT, retweets INT, replies INT
        mentions = tweet['entities']['user_mentions']
        if mentions:
            for m in mentions:
                keys = [tweet['id'], m['id'], tweet['created_at'][:len(tweet['created_at'])-20], 1, 1, 0, 0]
                try:
                    with self.con:
                        cursor = self.con.cursor()
                        cursor.execute("SELECT * from interactions where (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(m['id'])+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                        node = cursor.fetchone()
                        if node:
                            total = node[3]+1
                            partial = node[4]+1
                            cursor.execute("UPDATE interactions set weight = "+str(total)+" ,mentions = "+str(partial)+" WHERE (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(m['id'])+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                        else:
                            cursor.execute("INSERT INTO interactions VALUES (?,?,?,?,?,?,?)",keys)
                except Exception, e:
                    print "DB Error - insert_mentions: ", e

    def insert_retweet(self,tweet):
        #user_id INT, target_id INT, day DATE, weight INT, mentions INT, retweets INT, replies INT
        if tweet.get('retweeted_status', False):
            retweets = tweet['retweeted_status']
            keys = [tweet['id'], retweets['user']['id'], tweet['created_at'][:len(tweet['created_at'])-20], 1, 0, 1, 0]
            try:
                with self.con:
                    cursor = self.con.cursor()
                    cursor.execute("SELECT * from interactions where (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(retweets['user']['id'])+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    node = cursor.fetchone()
                    if node:
                        total = node[3]+1
                        partial = node[5]+1
                        cursor.execute("UPDATE interactions set weight = "+str(total)+" ,retweets = "+str(partial)+" WHERE (user_id = '"+str(tweet['id'])+"' AND target_id = '"+str(retweets['user']['id'])+"' AND day = '"+ tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    else:
                        cursor.execute("INSERT INTO interactions VALUES (?,?,?,?,?,?,?)",keys)
            except Exception, e:
                print "DB Error - insert_reply: ", e


    def insert_language_group(self,tweet):
        #lang TEXT, group_id TEXT, total INT
        keys = [tweet['lang'], "", 1]
        try:
            with self.con:
                cursor = self.con.cursor()
                cursor.execute("SELECT total from language_group WHERE ( lang='"+tweet['lang']+"' AND group_id ='"+""+"')")
                node = cursor.fetchone()
                if node:
                    total = node[0]+1
                    cursor.execute("UPDATE language_group set total = "+str(total)+" WHERE  ( lang='"+tweet['lang']+"' AND group_id ='"+""+"')")
                else:
                    cursor.execute("INSERT INTO language_group VALUES (?,?,?)",keys)
        except Exception, e:
            print "DB Error - language_group: ", e

    def insert_language_candidate(self,tweet):
        #lang TEXT, candidate_id INT, total INT
        keys = [tweet['lang'], 44101578, 1]
        try:
            with self.con:
                cursor = self.con.cursor()
                cursor.execute("SELECT total from language_candidate WHERE ( lang='"+tweet['lang']+"' AND candidate_id ='"+str(44101578)+"')")
                node = cursor.fetchone()
                if node:
                    total = node[0]+1
                    cursor.execute("UPDATE language_candidate set total = "+str(total)+" WHERE  ( lang='"+tweet['lang']+"' AND candidate_id ='"+str(44101578)+"')")
                else:
                    cursor.execute("INSERT INTO language_candidate VALUES (?,?,?)",keys)
        except Exception, e:
            print "DB Error - language_candidate: ", e

    def insert_hash_country(self,tweet):
        #text TEXT, country_id TEXT, day DATE, total INT
        hashtags = tweet['entities']['hashtags']
        for h in hashtags:
            hashtag = h['text']
            keys = [hashtag, tweet['lang'], tweet['created_at'][:len(tweet['created_at'])-20], 1]
            try:
                with self.con:
                    cursor = self.con.cursor()
                    cursor.execute("SELECT text, total from hash_country WHERE ( text='"+hashtag+"' AND country_id = '"+tweet['lang']+"' AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    node = cursor.fetchone()
                    if node:
                        total = node[1]+1
                        cursor.execute("UPDATE hash_country set total = "+str(total)+"  WHERE ( text='"+hashtag+"' AND country_id = '"+tweet['lang']+"' AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    else:
                        cursor.execute("INSERT INTO hash_country VALUES (?,?,?,?)",keys)
            except Exception, e:
                print "DB Error - insert_hash_country: ", e

    def insert_hash_group(self,tweet):
        #text TEXT, group_id TEXT, day DATE, total INT
        hashtags = tweet['entities']['hashtags']
        for h in hashtags:
            hashtag = h['text']
            keys = [hashtag, "ALDE", tweet['created_at'][:len(tweet['created_at'])-20], 1]
            try:
                with self.con:
                    cursor = self.con.cursor()
                    cursor.execute("SELECT text, total from hash_group WHERE ( text='"+hashtag+"' AND group_id = 'ALDE' AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    node = cursor.fetchone()
                    if node:
                        total = node[1]+1
                        cursor.execute("UPDATE hash_group set total = "+str(total)+"  WHERE ( text='"+hashtag+"' AND group_id = 'ALDE' AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    else:
                        cursor.execute("INSERT INTO hash_group VALUES (?,?,?,?)",keys)
            except Exception, e:
                print "DB Error - insert_hash_group: ", e

    def insert_hash_candidate(self,tweet):
        #text TEXT, candidate_id INT, day DATE, total INT
        hashtags = tweet['entities']['hashtags']
        for h in hashtags:
            hashtag = h['text']
            keys = [hashtag, 44101578, tweet['created_at'][:len(tweet['created_at'])-20], 1]
            try:
                with self.con:
                    cursor = self.con.cursor()
                    cursor.execute("SELECT text, total from hash_candidate WHERE ( text='"+hashtag+"' AND candidate_id = "+str(44101578)+" AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    node = cursor.fetchone()
                    if node:
                        total = node[1]+1
                        cursor.execute("UPDATE hash_candidate set total = "+str(total)+"  WHERE ( text='"+hashtag+"' AND candidate_id = "+str(44101578)+" AND day = '"+tweet['created_at'][:len(tweet['created_at'])-20]+"')")
                    else:
                        cursor.execute("INSERT INTO hash_candidate VALUES (?,?,?,?)",keys)
            except Exception, e:
                print "DB Error - insert_hash_group: ", e

