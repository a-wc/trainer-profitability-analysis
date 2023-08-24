import requests
from bs4 import BeautifulSoup
import re
import time
import concurrent.futures
import stockx

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

nike_regex = "[A-Za-z][A-Za-z]\d\d\d\d\-\d\d\d"
adidas_reebok_regex = "[A-Za-z][A-Za-z]\d\d\d\d|[A-Za-z]\d\d\d\d\d"
new_balance_regex = ""

asics_regex = "\d\d\d\d[A-Za-z]\d\d\d\-\d\d\d"
converse_regex = "\d\d\d\d\d\d[A-Za-z]"
puma_regex = "\d\d\d\d\d\d\-\d\d"
crocs_regex = "\d\d\d\d\d\d\-[A-Za-z0-9][A-Za-z0-9][A-Za-z0-9]"


with open("mesh_proxies.txt", 'r') as f:
    content = f.readlines()
    links = [row.strip() for row in content]
    proxies = {}
    proxies['http'] = links

# Scrapes a page and returns a list of dicts of data about each product:
# {"Product Link", "Image Link", "Price GBP", "Regex"}
def get_product_info(page_link):

    print("\n Scraping "+page_link+"...\n\n")

    # contains tuples in the form (sku_regex, product img link, price)
    product_info = []

    # get html content
    r = requests.get(page_link+"?from=0&max=20", headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")

    # navigate to product list
    main_product_list = soup.find('ul', class_="listProducts productList imageLazy")
    product_list = main_product_list.find_all('li', class_='productListItem')

    for product in product_list:

        # get the product brand
        product_title = product.find("span", class_ = "itemTitle").get_text()

        if "Nike" in product_title:
            regex = nike_regex
        elif "adidas" in product_title:
            regex = adidas_reebok_regex
        elif "Asics" in product_title:
            regex = asics_regex
        elif "Converse" in product_title:
            regex = adidas_reebok_regex
        elif "Puma" in product_title:
            regex = puma_regex
        elif "Crocs" in product_title:
            regex = crocs_regex
        else:
            regex = None

        # get the product price not on sale
        if product.find("span", class_="now") == None:
            product_price = product.find("span", class_="pri").get_text()
            
        # if product on sale
        else:
            product_price_tag = product.find("span", class_="now").get_text()
            if product_price_tag[11] == " ":
                product_price = product_price_tag[5:11]
            else:
                product_price = product_price_tag[5:12]

        # get the product image link
        product_image_link = product.find("source", type="image/webp")["data-srcset"]

        # returns several links so use the first
        product_image_link = product_image_link.split(" ")[0]

        # get the product link
        product_link =  product.find_all("a", href = True)[-1]['href']
        
        # add a tuple containing image link and price
        product_info.append({"Product Link": product_link, "Image Link": product_image_link, "Price GBP": product_price, "Regex": regex})

    return product_info

def get_product_sizes(product_link):

    url = "https://www.jdsports.co.uk" + product_link + "stock"

    r = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")

    buttons = soup.find_all("button")

    size_list = []
    
    for button in buttons:

        if button['title'] != "Out Of Stock":
            text = button.get_text()
            size = re.search("\d.\d|\d\d|\d", text)
            if size != None:
                size_list.append(size.group())

    size_list = size_list[:-1]
    
    return size_list

def get_all_product_sizes(product_info_list):

    executor = concurrent.futures.ProcessPoolExecutor(2)
    futures = [executor.submit(get_product_sizes, product["Product Link"]) for product in product_info_list]
    concurrent.futures.wait(futures)

    for i in range(len(product_info_list)):
        product_info_list[i]["Sizes"] = futures[i].result()
    
    return product_info_list



def get_sku(product_image_link, product_brand_regex):

    if product_brand_regex == None:
        sku = None
        return sku
    
    r = requests.get("https://lens.google.com/uploadbyurl?url="+product_image_link, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")

    # find brand name for sku look
    
    all_script_tags = soup.select('script')
    matched_images_data = ''.join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

    match = re.findall(product_brand_regex, matched_images_data)

    if len(match)==0:
        sku = None
        return sku

    
    match = [mat.upper() for mat in match]

    sku = max(set(match[0:8]), key=match[0:8].count)

    return sku

def get_all_skus(product_info_list):

    executor = concurrent.futures.ProcessPoolExecutor()
    futures = [executor.submit(get_sku, product["Image Link"], product["Regex"]) for product in product_info_list]
    concurrent.futures.wait(futures)

    # for i in range(len(product_info_list)):
    #     skus.append((futures[i].result()))

    for i in range(len(product_info_list)):
        product_info_list[i]["SKU"] = futures[i].result()
    
    return product_info_list

def scrape_page(page):


    product_info_list = get_product_info(page)
    product_info_list = get_all_skus(product_info_list)
    product_info_list = get_all_product_sizes(product_info_list)

    return product_info_list

 

if __name__ == '__main__':

    product_info = scrape_page("https://www.jdsports.co.uk/men/mens-footwear/brand/nike/sale/")

    product_info = stockx.get_all_product_urls(product_info)

    # for product in product_info:
    #     product["StockX URL"] = stockx.get_product_url(product["SKU"])

    print(product_info)
    # product_info = stockx.get_all_sales_info(product_info)

    







