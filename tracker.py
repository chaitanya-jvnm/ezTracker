#works only for flipkart now

#TODO : figure out amazon api and use it for amazon urls

#%%
import requests
from glob import glob
from bs4 import BeautifulSoup
# import pandas
from datetime import datetime
from time import sleep
import json

#%%
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

#%%
def main(url):
    page = requests.get(url,headers=HEADERS)
    soup = BeautifulSoup(page.content, features="lxml")

    #Product Name section
    try:
        #pName = soup.find(id='productTitle').get_text().strip() --Amazon
        pName = soup.find_all(class_="B_NuCI")[0].get_text().replace(u'\xa0', u' ').strip()
    except:
        pName = ''

    # Product price section
    try:
        # pPrice = float(soup.find(id='priceblock_ourprice').get_text().replace('.', '').replace('₹', '').replace(',', '.').strip()) --Amazon
        pPrice = soup.find_all(class_="_30jeq3")[0].get_text().strip()
    except:
        pPrice = ''
    
    #Product rating
    try:
        pRating = soup.find_all(class_="_3LWZlK")[0].get_text()
    except:
        pRating = ''

    #try:
        # soup.select('#availability .a-color-state')[0].get_text().strip() --Amazon availability
        # stock = 'Out of Stock'
    # except:
    #     stock = 'Available'

    #print( "[ Rating: " + pRating + " ]\n" + pName + "\n[ Price: " + pPrice + " ]")
    # print ('{ "name": "' + pName + '", "rating":"' + pRating + '", "price":"' + pPrice + '" }')
    return '{ "name": "' + pName + '", "rating":"' + pRating + '", "price":"' + pPrice + '" }'


#%%
# item = "https://www.amazon.in/Logitech-Lightspeed-Suspension-LIGHTSYNC-Technology/dp/B08HNCG8WQ/ref=sr_1_10_sspa?crid=3QA8S7TAU8UXS&dchild=1"
link = str('https://www.flipkart.com/ambrane-aqc-56-18-w-3-mobile-charger-detachable-cable/p/itm053fe47c4f26c?pid=ACCFNACQPFAQBHTE&lid=LSTACCFNACQPFAQBHTE7AIBOQ&marketplace=FLIPKART&srno=b_1_5&otracker=hp_omu_Deals%2Bof%2Bthe%2BDay_4_3.dealCard.OMU_NW53DUEZOI54_3&otracker1=hp_omu_SECTIONED_neo%2Fmerchandising_Deals%2Bof%2Bthe%2BDay_NA_dealCard_cc_4_NA_view-all_3&fm=neo%2Fmerchandising&iid=acf14168-0de3-4f65-af60-7cc22381d7d2.ACCFNACQPFAQBHTE.SEARCH&ppt=browse&ppn=browse&ssid=4dkfw756u34qbsow1613827233912')

#%%
product = json.loads(main(link))
print ( "[ Rating: " + product['rating'] + " ]\n" + product['name'] + "\n[ Price: " + product['price'] + " ]")
    
# %%
#testing block
