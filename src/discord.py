from .client import Client
from tls_client import response
from time import time
from typing import Union
from colorama import Fore
from base64 import b64encode, b64decode
from json import dumps, loads
from random import choice
import urllib.parse
import httpx
import websocket

class Discord:
    def __init__(self, proxy: str, token: str, xsup: str) -> None:
        cli = Client(proxy)

        self.session, self.headers, self.proxy, self.token, self.xsup = cli.session, cli.headers, cli.proxy, token, xsup
    
    @staticmethod
    def latest_js():
        try:
            return ( httpx.get(
                        "https://discord.com/app"
                        ).text.split(
                        '"></script><script src="/assets/'
                        )[2].split(
                        '" integrity'
                        )[0]
                    )
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
    
    @staticmethod
    def getBuildNum() -> str:
        req = httpx.get(
         f"https://discord.com/assets/{Discord.latest_js()}"
        )

        if req.status_code == 200:
            build_number = req.text.split('(t="')[1].split('")?t:"")')[0]

            return (
                 build_number
            )
    
    @staticmethod
    def getContextProperties(invite: str) -> Union[str, str]:
        try:
            req = httpx.get(
                f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true"
            ).json()
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return "", ""

        g = req["guild"]["id"]
        c = req["channel"]["id"]
        t = req["channel"]["type"]
        #Join Guild
        return g, b64encode(dumps({"location":"Accept Invite Page","location_guild_id":g,"location_channel_id":c,"location_channel_type":int(t)}).encode()).decode()
          
    def createDM(self, userID: str, guildID: str, channelID: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/"+guildID+"/"+channelID
        headers["x-context-properties"] = "e30="
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"

        js = {
            "recipients": [
                userID
            ]
        }

        try:
            req = self.session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 200:
            return True, req
        else:
            return False, req
    
    def closeDM(self, channelID: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"

        try:
            req = self.session.delete("https://discord.com/api/v9/channels/"+channelID+"?silent=false", headers=headers, proxy=self.proxy)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response

        if req.status_code == 200:
            return True, req
        else:
            return False, req
    
    def sendDM(self, channelID: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"

        js = {
            "content": message,
            #"flags": 0,
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "tts": False
        }

        try:
            req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/messages", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response

        if req.status_code == 200:
            return True, req
        else:
            return False, req
    
    def callWS(self, channelID: str):
        user_id = b64decode(self.token[0:24].encode()).decode()
        
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": self.token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))

        
        for i in range(10):
            js = loads(ws.recv())
            try:
                ses = js["d"]["session_id"]
                break
            except Exception as e:
                print(str(e))
        
        pd = {
            "op": 0,
            "d": {
                "server_id": channelID,
                "session_id": ses,
                "user_id": user_id,
                "video": False
            }
        }
        
        ws.send(dumps(pd))
        for i in range(10):
            js = ws.recv()
            
            print(js)
    
    def call(self, channelID: str):
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"

        js = {
            "recipients": None
        }

        try:
            req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/call/ring", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response

        if req.status_code == 204:
            return True, req
        else:
            return False, req

        
    def scrapeIDs(self, channelID: str) -> list:
        x = 0
        
        ids = open("scraped/IDs.txt", "a+")
        IDs = set()

        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID

        try:
            req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=100", headers=headers, proxy=self.proxy).json()
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return []
        
        for js in req:
            id = js["author"]["id"]
            mes_id = js["id"]
            bef = len(IDs)
            IDs.add(id)
            aft = len(IDs)

            if bef != aft:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Scraped {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} "+id)
                    ids.write(id+"\n")

        while x < 50:
            x += 1
            ids = open("scraped/IDs.txt", "a+")
            try:
                req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=100&before={mes_id}", headers=headers, proxy=self.proxy)
            except:
                ids.close()
                return IDs
            
            if req.status_code != 200:
                ids.close()
                return IDs
            
            req = req.json()
            for js in req:
                id = js["author"]["id"]
                bef = len(IDs)
                IDs.add(id)
                aft = len(IDs)

                if bef != aft:
                    print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}*{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Scraped {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} "+id)

                    ids.write(id+"\n")
            ids.close()
        
        return IDs
    
    def leave(self, guildID: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        
        payload = {
            "lurking": False
        }
        try:
            req = self.session.delete("https://discord.com/api/v9/users/@me/guilds/"+guildID, headers=headers, proxy=self.proxy, json=payload)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 204:
            return True, req
        else:
            return False, req
        
        
    def join(self, invite: str, context: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/invite/"+invite
        headers["x-context-properties"] = context
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"

        try:
            req = self.session.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, proxy=self.proxy, json={})
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response

        if req.status_code == 200:
            return True, req
        else:
            return False, req

    def sendMessage(self, channelID: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        js = {"content": message, "tts": "false"}
        try:
            req = self.session.post("https://discord.com/api/v9/channels/"+channelID+"/messages", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 200:
            return True, req
        else:
            return False, req
    
    def friendRequest(self, username: str) -> Union[bool, response.Response]:
        username, discriminator = username.split("#")
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-context-properties"] = "eyJsb2NhdGlvbiI6IkFkZCBGcmllbmQifQ=="
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        headers["referer"] = "https://discord.com/channels/@me"
        
        js = {"username": username, "discriminator": int(discriminator)}
        
        try:
            req = self.session.post("https://discord.com/api/v9/users/@me/relationships", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 204:
            return True, req
        else:
            return False, req
    
    def acceptRules(self, invite: str, guildID: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        #headers["referer"] = "https://discord.com/channels/@me"
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        try:
            req = self.session.post("https://discord.com/api/v9/guilds/"+guildID+"/member-verification?with_guild=false&invite_code="+invite, headers=headers, proxy=self.proxy)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        js = req.json()
        payload = js
        
        for i in range(len(payload["fields"])):
            payload["form_fields"][i]["response"] = "true"
        
        
        headers["authorization"] = self.token
        try:
            req = self.session.put(f"https://discord.com/api/v9/guilds/{guildID}/requests/@me", headers=headers, proxy=self.proxy, json=payload)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 201:
            return True, req
        else:
            return False, req
    
    def nickname(self, guildID: str, nickname: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        payload = {"nick": nickname}

        try:
            req = self.session.patch(f"https://discord.com/api/v9/guilds/{guildID}/members/@me" ,headers=headers, proxy=self.proxy, json=payload)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 200:
            return True,req
        else:
            return False,req

    @staticmethod
    def joinVC(guildID: str, channelID: str, token: str):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))
        ws.send(dumps({"op": 4,"d": {"guild_id": guildID,"channel_id": channelID, "self_mute": False,"self_deaf": True}}))
        #never close websocket infinite (let it just timeout itself)s

    @staticmethod
    def online(token: str):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))
    
    def getSessionID(self) -> str:
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": self.token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))

        for i in range(10):
            js = loads(ws.recv())
            
            try:
                return js["d"]["session_id"]
            except:
                pass
            
            
    def check(self) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        
        try:
            req = self.session.get("https://discord.com/api/v9/users/@me/settings", headers=headers, proxy=self.proxy)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 200:
            return True, req
        else:
            return False, req
    
    def bypass(self, clientID: str, guildID: str, redirectURL: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        
        js = {
            "authorize":   True,
		    "permissions": "0",
        }
        
        try:
            req = self.session.post("https://discord.com/api/v9/oauth2/authorize?client_id="+clientID+"&state="+guildID+"&redirect_uri="+redirectURL+"&response_type=code&scope=identify guilds.join", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        location = req.json()["location"]
        headers = {
            "accept":          "*/*",
		    "accept-encoding": "gzip, deflate, br",
		    "accept-language": "en-US;q=0.9,en-GB;q=0.8",
		    "content-type":    "application/json",
		    "sec-fetch-dest":  "empty",
		    "sec-fetch-mode":  "cors",
		    "sec-fetch-site":  "same-origin",
		    "sec-ch-ua":       '"Not_A Brand";v="99", "Google Chrome";v="108", "Chromium";v="108"',
		    "user-agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        
        try:
            req = self.session.post(location, headers=headers, proxy=self.proxy)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 307:
            return True, req
        else:
            return False, req
    
    def getButton(self, channelID: str, token: str):
        headers = self.headers
        
        headers["authorization"] = token
                
        try:
            req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50", headers=headers, proxy=self.proxy).json()
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return

        for i in req:
            try:
                message_id = i["id"]
                flags = i["flags"]
                custom_id = i["components"][0]["components"][0]["custom_id"]
                typee = i["components"][0]["components"][0]["type"]
                application_id = i["author"]["id"]
                break
            except:
                continue
        
        try:
            return application_id, typee, custom_id, flags, message_id
        except:
            return
    
    def button(self, application_id: str, typee: str, custom_id: str, flags: str, message_id: str, channelID: str, guildID: str) -> Union[bool, response.Response]: 
        sessionID = self.getSessionID()
        headers = self.headers
        
        headers["authorization"] = self.token
        
        js = {
            "application_id": application_id,
            "channel_id": channelID,
            "data": {
                "component_type": typee,
                "custom_id": custom_id,
            },
            "guild_id": guildID,
            "message_flags": flags,
            "message_id": message_id,
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "type": 3,
            "session_id": sessionID,
        }
        
        
        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID
        
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        try:
            req = self.session.post("https://discord.com/api/v9/interactions", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 204:
            return True, req
        else:
            return False, req
    
    def forum(self, guildID: str, channelID: str, title: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        js = {
            "applied_tags": [],
            "auto_archive_duration": 4320,
            "message": {
                "content": message,
            },
            "name": title,
        }
        
        try:
            req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/threads?use_nested_fields=true", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 201:
            return True, req
        else:
            return False, req
    
    def getSubIDS(self) -> list:
        s = []
        
        headers = self.headers
        
        headers["referer"] = "https://discord.com/channels/@me"
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        try:
            req = self.session.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=self.headers, proxy=self.proxy).json()
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return []
        
        for sub in req:
            s.append(sub["id"])
        
        return s 

    def boost(self, guildID: str, ID: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["referer"] = "https://discord.com/channels/@me"
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        try:
            req = self.session.put(f"https://discord.com/api/v9/guilds/{guildID}/premium/subscriptions", headers=headers, proxy=self.proxy, json={"user_premium_guild_subscription_slot_ids": [ID]})
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 201:
            return True, req
        else:
            return False, req
    
    def reaction(self, messageID: str, channelID: str, emoji: str) -> Union[bool, response.Response]:
        #"https://discord.com/api/v9/channels/"+channelID+"/messages/"+messageID+"/reactions/"+emo+"/%40me?location=Message&burst=false"
        
        headers = self.headers
        
        #headers["referer"] = "https://discord.com/channels/@me/"+channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        try:
            req = self.session.put("https://discord.com/api/v9/channels/"+channelID+"/messages/"+messageID+"/reactions/"+urllib.parse.quote(emoji)+"/%40me?location=Message&burst=false", headers=headers, proxy=self.proxy)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 204:
            return True, req
        else:
            return False, req
    
    def threads(self, channelID: str, guildID: str, title: str) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-debug-options"] = "bugReporterEnabled"
        headers["x-discord-locale"] =  "en-US"
        
        js = {
            "applied_tags": [],
            "auto_archive_duration": 4320,
            "name": title,
            "type": 11,
        }
        
        try:
            req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/threads", headers=headers, proxy=self.proxy, json=js)
        except Exception as e:
            print(f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}!{Fore.LIGHTMAGENTA_EX}]{Fore.LIGHTWHITE_EX} Error on making request {Fore.LIGHTMAGENTA_EX}->{Fore.LIGHTWHITE_EX} {str(e)}")
            return False, response.Response
        
        if req.status_code == 201:
            return True, req
        else:
            return False, req
    
    #fire code by bluestorm 🔥
    def checkServer(self, guildID: str) -> bool:
        headers = self.headers
        
        headers["authorization"] = self.token

        req = self.session.get("https://discord.com/api/v9/users/@me/affinities/guilds" , headers=headers,proxy=self.proxy).text

        if guildID in req:
            return True
        else:
            return False
