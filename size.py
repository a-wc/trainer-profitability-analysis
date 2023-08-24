import requests
from bs4 import BeautifulSoup
import re
import time
import concurrent.futures

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


with open("mesh_proxies.txt", 'r') as f:
    content = f.readlines()
    links = [row.strip() for row in content]
    proxies = {}
    proxies['http'] = links
    


def get_product_links_and_price(page_link):

    product_links_and_price = []

    r = requests.get(page_link+"?from=0&max=50", headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")
    
    main_product_list = soup.find('ul', class_="listProducts productList imageLazy")
    product_list = main_product_list.find_all('li', class_='productListItem')
  
    for product in product_list:
 
        # get link
        link = product.find("a", class_="itemImage imagePaddingBottom", href=True)
        product_link = "https://www.size.co.uk" + link['href']

        # get price
        if product.find("span", class_="now") == None:
            product_price_tag = product.find("span", class_="pri").get_text()
            # Strip "£"
            product_price = product_price_tag[1:]
            
        # if product on sale
        else:
            product_price_tag = product.find("span", class_="now").get_text()
            # strip "Now...£"
            product_price = product_price_tag[6:]

        tmp_dict = {"link": product_link, 'price': product_price}
        product_links_and_price.append(tmp_dict)

    return product_links_and_price

def get_sku_and_sizes_from_link(product_link):

    r = requests.get(product_link, headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.content, "lxml")
    # get sizes

    size_list = []

    div = soup.find('div', id="productSizeStock")
    buttons = div.find_all("button")
    for button in buttons:
        text = button.get_text().lstrip()
        # find where size stops
        i = 0
        while i<len(text):
            if text[i] == "\n":
                break
            i+=1
        size_list.append(text[:i])
        
    # get sku

    item_info = soup.find('div', id ="itemInfo")
    product_description_group = item_info.find('ul', class_='acitem')
    product_description = product_description_group.find('li').getText()

    pipe_index = product_description.find("|")

    sku = ""
    
    sku_invalid = False

    for i in range(pipe_index+2, len(product_description)):
        if product_description[i] == " ":
            sku_invalid = True
            break
        if re.match("[a-z]", product_description[i]):
            sku_invalid = True
            break
        if re.match("\n", product_description[i]):
            break
        sku += product_description[i]
    
    if sku_invalid == False:
        return sku, size_list
    else:
        return (None, None)
    
def get_sku_from_list(product_links_and_price):

    executor = concurrent.futures.ProcessPoolExecutor()
    futures = [executor.submit(get_sku_and_sizes_from_link, product_info['link']) for product_info in product_links_and_price]
    concurrent.futures.wait(futures)

    for i in range(len(product_links_and_price)):
        product_links_and_price[i]["sku"] = futures[i].result()[0]
        product_links_and_price[i]["sizes"] = futures[i].result()[1]
    
    return product_links_and_price

# if __name__ == "__main__":

#     prod_info_list = get_product_links_and_price("https://www.size.co.uk/mens/footwear/sale/")
#     prod_info_list = get_sku_from_list(prod_info_list)
    
#     print(prod_info_list)