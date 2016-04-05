#!/usr/bin/env python

"""
This module computes the rolling average vertex degree of a twitter
tweet hashtag graph.

# Written by Qingpeng Zhang for Insight Coding Challenge.

To make it really efficient, we use two data structures. One is a list of tuples, 
self.edges. Each tuple include the timestamp and the two hashtags for an edge. We always
put the edge tuples by the order of timestamp for easy searching. For inserting new edge, we scan the list
from the end(right to left), from the edge with the latest timestamp, until we find the appropirate position to 
insert the new edge. For removing old edges out of the 60s window, we scan the list from the
beginning(left to right), until we find the cutoff point. 
This can increase the efficiency significantly.

Also we use another data structure, a dictionary with edges and corresponding timestamps.
This is used for dealing with new edge that has alreay been in the graph. So we only need
to find the position of that edge in the list, and update the time stamp if necessary.


In our testing, it can finish the 10000 lines in about 5 seconds on my laptop.


Qingpen-lm:src qingpeng$ time python average_degree.py ../data-gen/tweets.txt >full_v2_run2.out

real	0m2.888s
user	0m2.648s
sys	0m0.087s




"""

from datetime import datetime
import sys
import json
import time
from collections import deque


class HashtagGraph:
    def __init__(self):
        self.edges = [] # list of tuple, with (time, from_node, to_node) for each edge
        self.nodes = {} # node with degree
        self.edges_dict = {} # dictionary with edges and time
        self.latest = 0
        self.window = 60
        self.edges_sum = 0
        self.nodes_sum = 0


    def scan_and_insert_edge(self, frm, to, c_time = 0):
        
        # for the first record or sequence of edges has been emptied
        if self.edges_sum == 0:
            self.insert_edge(frm, to, c_time, 0)
            
        else:
        # if this edge is already there 

            if self.edges_dict.has_key((frm,to)):

                # update the timestamp for this edge and nothing else will change
                if self.edges_dict[(frm,to)] < c_time: # if  require updating to newest time
                    self.update_edge(frm, to, c_time)

            
            else:
                # find position to insert the edge
                # if the tweet is the newest
                if c_time >= self.edges[-1][0]:
                
                    
                    self.insert_edge(frm, to, c_time,self.edges_sum )
            
                # if not, scan the sequence of edges backward, to find appropriate position to insert
                else:
            
                    for i in range(self.edges_sum - 1, -1, -1):
     #                   print "step2", i, c_time, self.edges[i][0]
                        if c_time < self.edges[i][0]:
                            if self.check_in_window(c_time):
                                self.insert_edge(frm, to, c_time, i-1)
                            break
    def update_edge(self, frm, to, c_time):
    # find the position for that existing edge
        position = self.edges.index((self.edges_dict[(frm,to)],frm,to))
        # update the time
        
        
        self.edges[position] = (c_time, frm, to)
        self.edges_dict[(frm,to)] = c_time
    # insert edge
    def insert_edge(self, frm, to, c_time, i):
    
            self.edges.insert(i, (c_time,frm,to))
            self.edges_dict[(frm,to)] = c_time
            
            self.edges_sum += 1
            if self.nodes.has_key(frm):
                self.nodes[frm] += 1
            else:
                self.nodes[frm] = 1
                self.nodes_sum  += 1
            if self.nodes.has_key(to):
                self.nodes[to] += 1
            else:
                self.nodes[to] = 1
                self.nodes_sum  += 1

    def remove_old_edges(self, c_time):
    # scan forward from the beginning  to find the position to cut off/discard
        for i in range(self.edges_sum):

            if self.edges[0][0] < c_time - self.window:

                self.nodes[self.edges[0][1]] -= 1
                self.nodes[self.edges[0][2]] -= 1
                if self.nodes[self.edges[0][1]] == 0:
                    self.nodes.pop(self.edges[0][1], None)
                    self.nodes_sum -= 1
                if self.nodes[self.edges[0][2]] == 0:
                    self.nodes.pop(self.edges[0][2], None)
                    self.nodes_sum -= 1

                self.edges_dict.pop((self.edges[0][1],self.edges[0][2])) # remove this edge from dictionary
                del self.edges[0]
                self.edges_sum -= 1


            else:

                break


    def read_tweet(self, line):
        twitter = json.loads(line)
        created_at = twitter.get('created_at', None)
        if not created_at:
            return None, None
        c_time = time.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y')

        c_time = time.mktime(c_time)

        hashtags_list = twitter.get('entities', {}).get('hashtags', [])

        hashtags = list(set(hash['text'] for hash in hashtags_list))

        return c_time, hashtags
        

    def process_tweet(self, line): # deal with one tweet
        c_time, hashtags = self.read_tweet(line)

        if c_time == None:
            return None

#         
        if self.check_in_window(c_time): # if the tweet
            if c_time > self.latest: # if the tweet is the latest
                self.latest = c_time
            if len(hashtags) > 1:
                self.add_hashtags(c_time, hashtags)
            self.remove_old_edges(c_time)

        return '{0:.2f}'.format(self.calculate_ave_degree())
        


    def calculate_ave_degree(self):
        
        try:
            return float(self.edges_sum*2)/self.nodes_sum
        except ZeroDivisionError:
            return 0.00

                
    def check_in_window(self, c_time): # if the tweet is out of window (too early)
        if (self.latest - c_time) >= self.window:
            return False
        else:
            return True
        
    def add_hashtags(self, c_time, hashtags):
        hashtags_sorted = sorted(hashtags)
        
        for i in range(len(hashtags_sorted)):
            for j in range(i+1, len(hashtags_sorted)):
                self.scan_and_insert_edge(hashtags_sorted[i], hashtags_sorted[j], c_time)
                

if __name__ == "__main__":

    graph =HashtagGraph()

    file_in_obj = open(sys.argv[1],'r')
    for line in file_in_obj:
#        print line
        average_degree = graph.process_tweet(line)
        if average_degree:
            print average_degree


