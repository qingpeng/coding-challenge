
""" A Python Class
A simple Python graph class, demonstrating the essential 
facts and functionalities of graphs.
"""

from datetime import datetime
import sys
import json
import time


class HashtagNode:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, time=0):
        self.adjacent[neighbor] = time

    def del_neighbor(self, neighbor):
        self.adjacent.pop(neighbor, None)
        
    def get_connections(self):
        return self.adjacent.keys()  

    def get_degree(self):
        return len(self.adjacent.keys())
        
        
    def get_id(self):
        return self.id

    def get_time(self, neighbor):
        return self.adjacent[neighbor]

class HashtagGraph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0
        self.latest = 0
        self.window = 60
    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = HashtagNode(node)
        self.vert_dict[node] = new_vertex
        return new_vertex
        
    def del_vertex(self, node):
        self.num_vertices = self.num_vertices - 1

        return self.vert_dict.pop(node, None)


    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, time = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], time)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], time)

    def del_edge(self, frm, to):
#        print "here",frm,to
        self.vert_dict[frm].del_neighbor(self.vert_dict[to])
        self.vert_dict[to].del_neighbor(self.vert_dict[frm])
        if self.vert_dict[frm].get_degree() == 0:
            self.del_vertex(frm)
        if self.vert_dict[to].get_degree() == 0:
            self.del_vertex(to)
        
        
    def get_vertices(self):
        return self.vert_dict.keys()


    def read_tweet(self, line):
        twitter = json.loads(line)
        created_at = twitter.get('created_at', None)
        if not created_at:
            return None, None
        c_time = time.strptime(created_at,'%a %b %d %H:%M:%S +0000 %Y')
#        print c_time
        c_time = time.mktime(c_time)
#        print c_time
        hashtags_list = twitter.get('entities', {}).get('hashtags', [])

        hashtags = list(set(hash['text'] for hash in hashtags_list))

        return c_time, hashtags
        

    def process_tweet(self, line): # deal with one tweet
        c_time, hashtags = self.read_tweet(line)
 #       print c_time, hashtags
        if c_time == None:
            return None
        if self.check_in_window(c_time): # if the tweet
            if c_time > self.latest: # if the tweet is the latest
                self.latest = c_time
            if len(hashtags) > 1:
                self.add_hashtags(c_time, hashtags)
            self.remove_old_hashtags(c_time)
        return '{0:.2f}'.format(self.calculate_ave_degree())
        
        
    def get_total_degree(self):
        sum_degree = 0
        for v in self:
            sum_degree += v.get_degree()
            
        return sum_degree
    def calculate_ave_degree(self):
        
        try:
            return float(self.get_total_degree())/len(self.get_vertices())
        except ZeroDivisionError:
            return 0.00
        

                
    def check_in_window(self, c_time): # if the tweet is out of window (too early)
        if (self.latest - c_time) >= self.window:
            return False
        else:
            return True
        
    def add_hashtags(self, c_time, hashtags):
 #       hashtags_sorted = sorted(hashtags)
        
        for i in range(len(hashtags)):
            for j in range(i+1, len(hashtags)):
                self.add_edge(hashtags[i], hashtags[j], c_time)
                
    def remove_old_hashtags(self, c_time):
        for v in self:
            for w in v.get_connections():
                if v.get_time(w) < c_time - self.window:
                    self.del_edge(v.id,w.id)
    
            


        
if __name__ == "__main__":

    graph =HashtagGraph()

    file_in_obj = open(sys.argv[1],'r')
    for line in file_in_obj:
#        print line
        average_degree = graph.process_tweet(line)
        if average_degree:
            print average_degree


