from base64 import b64encode
from json import dumps

def XSuperProperties(buildNum: int):
    return b64encode(dumps({"os":"Windows","browser":"Chrome","device":"","system_locale":"pl-PL","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36","browser_version":"108.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":buildNum,"client_event_source":None,"design_id":0}).encode()).decode()