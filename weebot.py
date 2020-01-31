#!/usr/bin/env python3

import socket, random, time, os, sys, glob, re
import config as c
import helpers as s

class quote:
    def __init__(self, cache, server='irc.freenode.net'):
        self.dir = cache + "/*.txt"
        self.cache = cache
        self.nick = 'StoatIncarnate'
        self.DOB = time.time()
        self.age = 0 #seconds
        self.sock = socket.socket()
        self.listener = self.sock.makefile(mode='rw', buffering=1, encoding=c.ce, newline='\r\n')
        self.scripts = []
        self.quotes = []
        self.files = glob.glob(self.dir)
        self.status = self.status()
        self.status.serv = server
        self.status.port = 6667
        self.status.acquainted = {"#stoattalk":False}
        self.status.muzzled = False
        self.status.connected = False
    class status:
        def isAcquainted(self,channel):
            return self.acquainted[channel]
    def connect(self):
        self.sock.connect((self.status.serv, self.status.port))
        self.status.connected = True
    def join(self, channel):
        j_str = "JOIN "+ channel
        if channel not in self.status.acquainted:
            self.status.acquainted[channel] = False
        print(j_str, file=self.listener)
    def identify(self):
        print('NICK', self.nick, file=self.listener)
        print('USER', self.nick, self.nick, self.nick, ':'+self.nick, file=self.listener)
        i_str = "NS IDENTIFY " + c.password +"\r\n"
        print(i_str, file = self.listener)
    def message(self, msg, chan):
        self.sock.send(bytes("PRIVMSG "+chan+" :"+msg+"\n", c.ce))
    def greet(self, chan):
        greeting = "Konichiwa. Type '!info' for information on how I can be of service. Available scripts: "
        for f in self.files:
            greeting += "'"+f+"'" + " "
        greeting.strip(", ")
        self.message(greeting, chan)
    def load(self):
        self.scripts = [s.vectorizetext(i) for i in self.files]
        self.files = [i.strip(self.cache).strip('.txt').strip('/') for i in self.files]
        for script in self.scripts:
            for quote in script:
                self.quotes.append(quote.lower())
    def pong(self, line):
        print("PONG :" + line.split(':')[1], file=self.listener)
    def getQuote(self, line):
        line = line.lower().replace("!find", "")
        line = line.split(':')[-1].strip()
        qs = self.quotes.copy()
        quote = s.find(line, qs)
        msg = "Input was not detailed enough to isolate a quote. Please include more of the quote."
        if (quote == -1):
            self.message(msg, c.channel)
            return
        elif (isinstance(quote, list)):
            err = "Couldn't isolate quote. It might be one of these...\n"
            self.message(err, c.channel)
            if len(quote) > 5:
                quote = quote[0:5]
            for q in quote:
                self.message("-    "+q, c.channel)
            return
        i = 0
        for script in self.scripts:
            for q in script:
                if q.lower() == quote:
                    self.message(q, c.channel)
                    return
        self.message(msg, c.channel)
    def follow(self, line):
        line = line.lower().replace("!follow", "")
        line = line.split(':')[-1].strip()
        qs = self.quotes.copy()
        quote = s.find(line, qs)
        if (quote == -1):
            msg = "Input was not detailed enough to isolate a quote. Please include more of the quote."
            self.message(msg, c.channel)
        elif (isinstance(quote, list)):
            self.message("Which quote did you mean? Indicate by sending the index (starting at 0) preceeded by the '!' operator (e.g. '!3')")
            for q in quote:
                self.message(q, c.channel)
            return quote
        i = 0
        for script in self.scripts:
            for q in script:
                if q.lower() == quote:
                    j = script.index(q)
                    self.message(script[j+1], c.channel)
    def sample(self, line):
        line = line.replace("!sample", "").strip()
        for i in range(0, len(self.files)):
            if self.files[i] in line:
                self.message(random.choice(self.scripts[i]), c.channel)
                return
        msg = "Input did not match any existing script names. Please try again."
        self.message(msg, c.channel)
    def info(self):
        cmds = []
        f = "List of commands:\n\n"
        cmds.append("    stoat : gives info on me -- usage : !stoat\n\n\n")
        cmds.append("    sample : selects random quote from script bank -- usage : !sample <script name>\n\n\n")
        cmds.append("    find : selects closest match between input and available quotes -- usage : !find <input>\n\n\n")
        cmds.append("    follow : selects the next chronological quote from the best match in !find -- usage : !follow <input>\n\n\n")
        cmds.append("    quiet : puts me into sleep mode -- usage : !quiet\n\n\n")
        cmds.append("    listen : brings me out of sleep mode -- usage : !listen\n\n\n")
        self.message(f, c.channel)
        for cmd in cmds:
            self.message(cmd, c.channel)
    def choose(self, line):
        if "PING" in line:
            self.pong(line)
        elif "!info" in line:
            self.info()
        elif "!find" in line:
            self.getQuote(line)
        elif "!follow" in line:
            self.follow(line)
        elif "!sample" in line:
            self.sample(line)
        elif "!quiet" in line:
            self.status.muzzled = True
    def listen(self):
        for line in self.listener:
            line = line.strip()
            if "!die" in line:
                self.die()
            elif "!listen" in line:
                if not self.status.muzzled:
                    self.message("I was listening already, asshole...", c.channel)
                self.status.muzzled = False
            self.age = time.time() - self.DOB
            if self.age > 15:
                if (not self.status.isAcquainted(c.channel)):
                    self.greet(c.channel)
                    self.status.acquainted[c.channel] = True
            if not self.status.muzzled:
                self.choose(line)
    def die(self):
        self.message("Yeah fuck off anyways", c.channel)
        print("Someone killed StoatIncarnate")
        exit()
