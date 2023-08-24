import size
import stockx
import time
from random import uniform

def get_all_product_info(page_link):

    prod_info_list = size.get_product_links_and_price(page_link)
    prod_info_list = size.get_sku_from_list(prod_info_list)
    
    return prod_info_list

def get_product_sales_data(product_info):

    url = stockx.get_product_url(product_info['sku'])

    # product not on stockx, invalid sku on size
    if url == None:
        return None
    
    return stockx.scrape_product(url, product_info['sizes'])


def determine_profitability(product_info, stockx_data):

    if stockx_data == None:
        return []
    profitable_sizes = []
    for size in stockx_data:

        uk_size = size['sizeChart']['displayOptions'][1]['size'][3:]

        if uk_size == "6 (EU 40)":
            uk_size = '6'

        last_sale = stockx_data['market']['statistics']['lastSale']['amount']
        # lvl1 fees
        last_sale_payout = round(float(last_sale)*0.87-4, 2)

        if last_sale_payout > float(product_info['price']):
            profitable_sizes.append(uk_size)

    return (product_info, profitable_sizes)

if __name__ == "__main__":

    prod_info = get_all_product_info("https://www.size.co.uk/mens/footwear/sale/")

    for prod in prod_info:

        sales_data= get_product_sales_data(prod)
        time.sleep(round(uniform(0.5,1.5), 2))