from src.discord import Discord
from src.utils import XSuperProperties
from colorama import Fore, init
import random
import os
import time
import ctypes
import threading

init()
width = os.get_terminal_size().columns

class MassDM:
    def __init__(self):
        build_num = Discord.getBuildNum()
        print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Build number {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {build_num}")
        self.xsuper = XSuperProperties(int(build_num))
        time.sleep(1)
        self.tokens = open("data/tokens.txt").read().splitlines()
        self.proxies = open("data/proxies.txt").read().splitlines()
        self.dms, self.fails = 0, 0
    
    def spammerDM(self, message: str, guildid: str, channelid: str, userid: str, token: str):
        dc = Discord(random.choice(self.proxies), token, self.xsuper)
        st, resp = dc.createDM(userid, guildid, channelid)
        if st:
            cr = resp.json()["id"]
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Created channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
        else:
            cr = resp.json()["message"]
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to create channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
            return  
            
        while True:
            st, resp = dc.sendDM(cr, message)
                
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}${Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Sent DM {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {message}")
            else:
                a = resp.json()["message"]
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to send DM {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {a}")
                
                if "captcha" in a or "You need to verify" in a or "Unautorized" in a or "Cannot send" in a:
                    return
            
        
    def massDM(self, message: str, guildid: str, channelid: str, close: bool, IDs: list, tokens: list):
        IDsSave = IDs.copy()

        x = 0
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            
            while True:
                if x >= len(IDs):
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Ran out of IDs!")
                    return

                st, resp = dc.createDM(IDs[x], guildid, channelid)
                if st:
                    cr = resp.json()["id"]
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Created channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
                else:
                    cr = resp.json()["message"]
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to create channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
                    continue
                
                st, resp = dc.sendDM(cr, message)

                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}${Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Sent DM {Fore.LIGHTMAGENTA_EX}to{Fore.LIGHTWHITE_EX} {IDs[x]}")
                    self.dms += 1
                    IDsSave.remove(IDs[x])
                else:
                    m = resp.json()
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to send DM, Response {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
                    self.fails += 1

                if close:
                    st, resp = dc.closeDM(cr)
                    if st:
                        print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Closed DM")
                    else:
                        m = resp.json()["message"]
                        print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to close DM, Response {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
                x += 1
                
                time.sleep(3)
        
        IDss = open("scraped/IDs.txt", "w")
        for id in IDsSave:
            IDss.write(id + "\n")
        IDss.close()


    def scrape(self, token: str, channelID: str):
        dc = Discord(random.choice(self.proxies), token, self.xsuper)
        IDs = dc.scrapeIDs(channelID)
        
        print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Scraped {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(len(IDs))} IDs")
        
    def join(self, invite: str, context: str, tokens: list, guildID: str = ""):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.join(invite, context)
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Joined {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {invite}")
            else:
                try:
                    m = resp.json()
                except:
                    m = resp.text
                
                if resp.status_code == 400:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to join {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} Captcha")
                else:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to join {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
            
            if guildID != "":
                st, resp = dc.acceptRules(invite, guildID)
                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Bypassed rules {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {invite}")
                else:
                    m = resp.json()
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to bypass rules {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
                
    
    def leave(self, guildID: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.leave(guildID)
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Left {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {guildID}")
            else:
                m = resp.json()["message"]
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to leave {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
    
    def friend(self, username: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.friendRequest(username)
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Sent friend request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {username}")
            else:
                m = resp.json()
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to send friend request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")     
    
    def spammer(self, channelID: str, message: str, token: str, massping: bool = False, pings: int = 0):
        spl = channelID.split(",")
        ids = open("scraped/IDs.txt", "r").read().splitlines()
        dc = Discord(random.choice(self.proxies), token, self.xsuper)
        

        while True:
                for i in range(pings):
                    msg = message + f" | <@{random.choice(ids)}>"
                
                if pings != 0:
                    st, resp = dc.sendMessage(random.choice(spl), msg)
                else:
                    st, resp = dc.sendMessage(random.choice(spl), message)
                    
                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Sent message {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {message}")
                else:
                    m = resp.json()["message"]
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to send message {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
                    
                    if "You need to verify" in m or "Unauthorized" in m or "Missing Access" in m:
                        return
                    
    
    def checker(self, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.check()
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Unlocked {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")
                self.v.append(token)
            else:
                m = resp.json()["message"]
                if m == "401: Unauthorized":
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Invalid {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")
                else:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Locked {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")    
    
    def verifyBypass(self, clientID: str, guildID: str, redirectURL: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.bypass(clientID, guildID, redirectURL)
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Verified {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")
            else:
                m = resp.json()
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to verify {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
    
    def button(self, messageshit: list, channelID: str, guildID: str, amount: int, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            
            for i in range(amount+1):
                st, resp = dc.button(*messageshit, channelID, guildID)
                
                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Clicked button!")
                else:
                    m = resp.json()
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to click button {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")

    
    def forumFlooder(self, channelID: str, guildID: str, message: str, title: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            
            while True:
                st, resp = dc.forum(guildID, channelID, title, message)
                
                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Created post")
                else:
                    m = resp.json()
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to create post {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")

    def boostServer(self, guildID: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            subs = dc.getSubIDS()
            
            if subs == []:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Token has no boosts {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")
            
            for sub in subs:
                st, resp = dc.boost(guildID, sub)
                
                if st:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Boosted server!")
                else:
                    m = resp.json()
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to boost server {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")

    def reactionAdder(self, messageID: str, channelID: str, emoji: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.reaction(messageID, channelID, emoji)
                
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Added reaction!")
            else:
                m = resp.json()
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to add reaction {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
    
    def threads(self, channelID: str, guildID: str, title: str, tokens: list, message: str = ""):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.threads(channelID, guildID, title)
                
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Created Thread!")
                idd = resp.json()["id"]
                    
                if message != "":
                    x = threading.Thread(target=self.spammer, args=(idd, message,token,))
                    self.threadss.append(x)
                    x.start()
                    
            else:
                m = resp.json()
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to create thread {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
    
    def nickname(self, guildID: str, nickname: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.nickname(guildID, nickname)
            
            if st:
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Changed nickname!")
            else:
                m = resp.json()
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to change nickname {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {m}")
    
    def caller(self, guildID: str, channelID: str, userID: str, tokens: list):
        for token in tokens:
            dc = Discord(random.choice(self.proxies), token, self.xsuper)
            st, resp = dc.createDM(userID, guildID, channelID)
            if st:
                cr = resp.json()["id"]
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Created channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
            else:
                cr = resp.json()["message"]
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to create channel {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
                continue
            
            st, resp = dc.call(cr)
            if st:
                dc.callWS(cr)
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Calling {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
            else:
                cr = resp.json()["message"]
                print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Failed to call {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {cr}")
                

    def split_list(self, a, n):
        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    
    def banner(self, options: bool):
        os.system("cls")
        if options == False:
            b = f"""
    __  __ _____           _ {Fore.LIGHTWHITE_EX} ____  
    |  \/  |_   _|__   ___ | |{Fore.LIGHTWHITE_EX}|___ \ 
    | |\/| | | |/ _ \ / _ \| |{Fore.LIGHTWHITE_EX}  __) |
    | |  | | | | (_) | (_) | |{Fore.LIGHTWHITE_EX} / __/ 
    |_|  |_| |_|\___/ \___/|_|{Fore.LIGHTWHITE_EX}|_____|"""
            banner = b.split("\n")
            for x in banner:
                print(" " * ((width//2)-(len(x)//2)) + Fore.LIGHTMAGENTA_EX + x)
        else:
            w = Fore.LIGHTWHITE_EX
            m = Fore.LIGHTMAGENTA_EX
            b = f"""
    __  __ _____           _ {w} ____  
    |  \/  |_   _|__   ___ | |{w}|___ \ 
    | |\/| | | |/ _ \ / _ \| |{w}  __) |
    | |  | | | | (_) | (_) | |{w} / __/ 
    |_|  |_| |_|\___/ \___/|_|{w}|_____|
            
                                        {m}[{w}1{m}]{w} Mass DM              {m}[{w}9{m}]{w} Verify Bypass
                                        {m}[{w}2{m}]{w} Scraper              {m}[{w}10{m}]{w} Button Clicker
                                        {m}[{w}3{m}]{w} Joiner               {m}[{w}11{m}]{w} Forum Flooder
                                        {m}[{w}4{m}]{w} Leaver               {m}[{w}12{m}]{w} Boost Server
                                        {m}[{w}5{m}]{w} Spammers             {m}[{w}13{m}]{w} Reaction Adder
                                    {m}[{w}6{m}]{w} Checker              {m}[{w}14{m}]{w} Onliner
                                {m}[{w}7{m}]{w} VC Joiner            {m}[{w}15{m}]{w} ???
                                {m}[{w}8{m}]{w} Nickname Changer     {m}[{w}16{m}]{w} ???
            """
            banner = b.split("\n")
            for x in banner:
                print(" " * ((width//2)-(len(x)//2)) + Fore.LIGHTMAGENTA_EX + x)
    
    def start(self):
        while True:
            op = f"""
            
            """
            self.banner(options=True)

            options = op.split("\n")
            for x in options:
                #print(" " * ((width//2)-(len(x)//2)+2) + Fore.LIGHTMAGENTA_EX + x)
                continue
            cho = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Option > ")

            if cho == "1":
                tkns = self.tokens.copy()
                IDs = open("scraped/IDs.txt").read().splitlines()
                calc = len(IDs) / len(self.tokens)
                
                if calc < 1:
                    calc = len(self.tokens) / len(IDs)
                
                a = 0
                while calc > 1:
                    tkns.remove(tkns[a])
                    calc = IDs / len(tkns)
                    a += 1
                    
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{calc}) > ")
                
                ids = self.split_list(IDs, int(calc))
                tokens = self.split_list(self.tokens, int(calc))
                mes = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message > ")
                g = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                c = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                close = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Close DM (Y/N) > ")
                if close == "Y" or close == "y":
                    cl = True
                else:
                    cl = False
                
                threads = []
                asd = 0
                for x in tokens:
                    a = threading.Thread(target=self.massDM, args=(mes, g, c, cl, ids[asd], x))
                    threads.append(a)
                    a.start()
                    asd += 1
                
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "2":
                tkn = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Token > ")
                cha = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                self.scrape(tkn, cha)
            
            elif cho == "3":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                inv = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Invite > ")
                byp = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Bypass rules (Y/N) > ")
                delay = int(input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Delay (s) > "))
               
                context, guildID = Discord.getContextProperties(inv)
                
                if delay == 0:
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        if byp == "Y" or byp == "y":
                            a = threading.Thread(target=self.join, args=(inv, context, x, guildID))
                        else:
                            a = threading.Thread(target=self.join, args=(inv, context, x))
                            
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                else:
                    for token in self.tokens:
                        self.join(inv, context, [token])
                        time.sleep(delay)
                
                time.sleep(10)
            
            elif cho == "4":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                g = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                
                tokens = self.split_list(self.tokens, int(threads))
                
                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.leave, args=(g, x))
                    threads.append(a)
                    a.start()
                
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "5":
                self.banner(options=False)
                print()
                print(" " * ((width//2)-(len(x)//2)-5) + Fore.LIGHTMAGENTA_EX + f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}1{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel Spammer")
                print(" " * ((width//2)-(len(x)//2)-5) + Fore.LIGHTMAGENTA_EX + f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}2{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads Spammer")
                print(" " * ((width//2)-(len(x)//2)-5) + Fore.LIGHTMAGENTA_EX + f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}3{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Friend Request Spammer")
                print(" " * ((width//2)-(len(x)//2)-5) + Fore.LIGHTMAGENTA_EX + f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}4{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} DM Spammer\n")
                cho = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Option > ")
                
                if cho == "1":
                    message = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message > ")
                    c = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel IDs (separated with commas) > ")
                    mp = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Mass Ping (Y/N) > ")
                    if mp == "Y" or mp == "y":
                        mp = True
                        pings = int(input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Amout of pings per message > "))
                    else:
                        pings = 0
                        mp = False
                    
                    threads = []
                    for x in self.tokens:
                        a = threading.Thread(target=self.spammer, args=(c, message, x, mp, pings))
                        threads.append(a)
                        a.start()
                
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                
                    time.sleep(3)
                
                elif cho == "2":
                    threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                    title = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Title > ")
                    g = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                    c = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                    autospam = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Spam in thread (Y/N) > ")
                    
                    if autospam == "Y" or autospam == "y":
                        message = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message > ")
                    else:
                        message = ""
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    self.threadss = []
                    for x in tokens:
                        a = threading.Thread(target=self.threads, args=(c, g, title, x, message))
                        self.threadss.append(a)
                        a.start()

                    time.sleep(1)
                    
                    while self.threadss != []:
                        for x in self.threadss:
                            if not x.is_alive():
                                x.join()
                                self.threadss.remove(x)
                
                    time.sleep(3)
                
                elif cho == "3":
                    threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                    username = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Username (someone#0000) > ")
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.friend, args=(username, x))
                        threads.append(a)
                        a.start()
                
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                
                    time.sleep(3)
                
                elif cho == "4":
                    message = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message > ")
                    u = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} User ID > ")
                    g = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                    c = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                    
                    threads = []
                    for x in self.tokens:
                        a = threading.Thread(target=self.spammerDM, args=(message, g, c, u, x))
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                
                    time.sleep(3)

            elif cho == "6":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")

                tokens = self.split_list(self.tokens, int(threads))
                
                self.v = []
                
                threads = []
                f = open("data/tokens.txt", "w")
                f.close()

                for x in tokens:
                    a = threading.Thread(target=self.checker, args=(x,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                f = open("data/tokens.txt", "a+")
                for token in self.v:
                    f.write(token+"\n")
                
                f.close()

                
                time.sleep(3)
            
            elif cho == "7":
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                channelID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")

                for token in self.tokens:
                    Discord.joinVC(guildID, channelID, token)
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Joined VC {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")
                
                time.sleep(3)

            elif cho == "8":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                nickname = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Nickname > ")
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                
                tokens = self.split_list(self.tokens, int(threads))

                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.nickname, args=(guildID, nickname, x,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "9":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                clientID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Client ID > ")
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                redirectURL = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Redirect URL > ")
                
                tokens = self.split_list(self.tokens, int(threads))

                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.verifyBypass, args=(clientID, guildID, redirectURL, x,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "10":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                channelID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                amount = int(input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Amount per token > "))

                tokens = self.split_list(self.tokens, int(threads))
                
                tkn = random.choice(self.tokens)
                dc = Discord(random.choice(self.proxies), tkn, self.xsuper)
                messageshit = dc.getButton(channelID, tkn)
                
                while messageshit == None:
                    tkn = random.choice(self.tokens)
                    dc = Discord(random.choice(self.proxies), tkn, self.xsuper)
                    messageshit = dc.getButton(channelID, tkn)
                
                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.button, args=(messageshit, channelID, guildID, amount, x,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "11":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                channelID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                title = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Title > ")
                message = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message > ")
                
                tokens = self.split_list(self.tokens, int(threads))
                
                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.forumFlooder, args=(channelID, guildID, message,title, x,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)

            elif cho == "12":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                guildID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")

                tokens = self.split_list(self.tokens, int(threads))
                
                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.boostServer, args=(guildID,x ,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)

            elif cho == "13":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                message = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Message ID > ")
                channelID = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                emoji = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Emoji > ")
                
                tokens = self.split_list(self.tokens, int(threads))
                
                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.reactionAdder, args=(message, channelID, emoji, x ,))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "14":
                for token in self.tokens:
                    Discord.online(token)
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Online {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {token[:24]}...")

                time.sleep(3)
            
            elif cho == "15":
                threads = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Threads (1-{len(self.tokens)}) > ")
                u = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} User ID > ")
                g = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Guild ID > ")
                c = input(" " * ((width//3)-(len(x)//2)) +f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}>{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Channel ID > ")
                
                tokens = self.split_list(self.tokens, int(threads))

                threads = []
                for x in tokens:
                    a = threading.Thread(target=self.caller, args=(g, c, u, x))
                    threads.append(a)
                    a.start()
                    
                while threads != []:
                    for x in threads:
                        if not x.is_alive():
                            x.join()
                            threads.remove(x)
                
                time.sleep(3)
            
            elif cho == "69":
                print('stfu')
                time.sleep(3)
            


                    

MassDM().start()