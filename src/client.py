from tls_client import Session
import binascii
import os
import random

class Client:
    def __init__(self, proxy: str) -> None:
        self.headers = {
			"accept":             "*/*",
			"accept-language":    "en-US;q=0.8,en;q=0.7",
			"content-type":       "application/json",
			"host":               "discord.com",
			"origin":             "https://discord.com",
			"sec-ch-ua":          '"Chromium";v="108", "Google Chrome";v="108", "Not;A=Brand";v="99"',
			"sec-ch-ua-mobile":   "?0",
			"sec-ch-ua-platform": '"Windows"',
			"sec-fetch-dest":     "empty",
			"sec-fetch-mode":     "cors",
			"sec-fetch-site":     "same-origin",
			"user-agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        self.session = Session(client_identifier="chrome_108")
        self.proxy = "http://" + proxy

        #self.session.get("https://discord.com", headers=self.headers, proxy=self.proxy)
        x = self.session.get("https://discord.com", headers=self.headers, proxy=self.proxy).text
        self.headers["cookie"] = "; ".join(f"{k}={v}" for k,v in self.session.cookies.items())