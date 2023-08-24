from random import choice

# used to generate random http headers to avoid detection

USER_AGENTS = [
    'Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/57.0.2987.110 '
     'Safari/537.36',  
    'Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.79 '
     'Safari/537.36',  
    'Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.91 '
     'Safari/537.36', 
    'Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/62.0.3202.89 '
     'Safari/537.36', 
    'Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/63.0.3239.108 '
     'Safari/537.36',  
]

SEC_FETCH_SITES = ['cross-site', 'none']

ORIGINS = ["https://stockx.com", 
           "https://www.google.com", 
            "http://www.bing.com/",
            "https://yahoo.com/",
            "https://www.azlyrics.com/",
            "https://www.dogpile.com/",
            "http://www.yippy.com",
            "https://yandex.com/"]

LANGUAGES = ['en-GB', 
             'en-GB,en-US;q=0.9',
             "en-GB,en-US;q=0.9,en;q=0.8",
             "en-GB,en;q=0.9,en-US;q=0.8"]
def get_header():

    origin = choice(ORIGINS)

    sec_fetch_site = 'same-site'
    if origin != "https://stockx.com":
        sec_fetch_site = choice(SEC_FETCH_SITES)
        
    headers = {
    "Accept": "*/*",
    "Accept-Language": choice(LANGUAGES),
    "Connection": "keep-alive",
    "Content-Type": "text/plain",
    "Origin": origin,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": sec_fetch_site,
    "User-Agent" : choice(USER_AGENTS),
    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"'}

    return headers
