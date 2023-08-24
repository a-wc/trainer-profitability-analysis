import json
import requests
from bs4 import BeautifulSoup
import re
import header_generator
import time 
from random import choice

from nested_lookup import nested_lookup
from parsel import Selector

with open("mesh_proxies.txt", 'r') as f:
    content = f.readlines()
    links = [row.strip() for row in content]
    proxies = {}
    proxies['http'] = links

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

SEC_FETCH_SITES = ['cross-site', 'cross-origin', 'same-site', 'none']
 

def get_product_url(sku):

    print(sku)
    if sku == None:
        return None
    
    url = "https://stockx.com/en-gb/search?s=" + sku

    headers = header_generator.get_header()
    r = requests.get(url, headers = headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")
    div = soup.find("div", class_="css-xzkzsa", id="browse-grid")

    if div == None:
        # see if blocked by captcha
        if soup.find('span', id="challenge-error-text") != None:
            print("retrying")
            return get_product_url(sku)
        print("cant find link")
        return None
    
    url_ending = div.find("a")['href']

    return "https://stockx.com" + url_ending

def parse_nextjs(html: str) -> dict:
    """extract nextjs cache from page"""
    selector = Selector(html)
    data = selector.css("script#__NEXT_DATA__::text").get()
    if not data:
        data = selector.css("script[data-name=query]::text").get()
        data = data.split("=", 1)[-1].strip().strip(";")
    data = json.loads(data)
    return data


def scrape_product(url, sizes):
    """scrape a single stockx product page for product data"""
    # response = client.get(url)
    print(url)
    count = 0

    headers = header_generator.get_header()
    response = requests.get(url, headers=headers, proxies=proxies)

    while response.status_code != 200 and count<100:
        response= requests.get(url, headers=headers, proxies=proxies)
        count+=1
        print(f"Failed {count} times")
    data = parse_nextjs(response.text)
    # extract all products datasets from page cache
    products = nested_lookup("product", data)
    # find the current product dataset
    try:
        product = next(p for p in products if p.get("urlKey") in str(response.url))
    except StopIteration:
        raise ValueError("Could not find product dataset in page cache", response)
    
    sales_info = product['variants']

    available_sizes_info = []

    for variant in sales_info:
        print(variant)
        
        # one-size product so likely an error
        if variant['sizeChart']['baseSize'] == '':
            continue
        try:
        # get uk size, omit "UK"
            uk_size = variant['sizeChart']['displayOptions'][1]['size'][3:]
        # uk sizes not included sometime
        except IndexError:
            # check if size is us m
            if variant['sizeChart']['baseType'] == "us m":
                    us_size = variant['sizeChart']['displayOptions'][0]['size'][5:]
            # handle childs sizing, will throw error when converting
            elif variant['sizeChart']['baseSize'][-1] == "C" or variant['sizeChart']['baseSize'][-1] == "K":
                # us_size = variant['sizeChart']['displayOptions'][0]['size'][3:-1]
                return []
            else:
                us_size = variant['sizeChart']['displayOptions'][0]['size'][3:]

            # handle conversions from us size
            if re.search("nike", url) != None and float(us_size) >= 7:
                uk_size = float(us_size) - 1
            else:
                uk_size = float(us_size) - 0.5
            
            if uk_size % 1 == 0:
                uk_size = str(int(uk_size))
            else:
                uk_size = str(uk_size)

        if uk_size in sizes:
            available_sizes_info.append(variant)

        # have to check if size is uk 6 as sX returns 6 (EU 40)
        if uk_size == "6 (EU 40)" and '6' in sizes:
            available_sizes_info.append(variant)

    return available_sizes_info


