from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None


def get_chrome_service():
    custom_path = os.environ.get('CHROMEDRIVER_PATH')
    if custom_path and os.path.exists(custom_path):
        return Service(executable_path=custom_path)
    if ChromeDriverManager is not None:
        return Service(executable_path=ChromeDriverManager().install())
    raise RuntimeError(
        'ChromeDriver not found. Set CHROMEDRIVER_PATH or install webdriver-manager.'
    )


def get_flipkart_url(product_name):
    product_name = product_name.replace(' ', '+')
    return f'https://www.flipkart.com/search?q={product_name}&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_2_10_na_na_ps&otracker1=AS_QueryStore_OrganicAutoSuggest_2_10_na_na_ps&as-pos=2&as-type=RECENT&suggestionId={product_name}%7CMobiles&requestId=f3a4c0b8-6573-49da-b5d9-8f6c45b6a844&as-backfill=on'

def get_list_of_text_from_webdriver_obj(webdriver_obj):
    li = []
    for i in webdriver_obj:
        li.append(i.text)
    return li

def get_list_of_prices_from_webdriver_obj(webdriver_obj, list_of_indexes_having_no_price):
    li = []
    for i in range(len(webdriver_obj)):
        if i in list_of_indexes_having_no_price:
            li.append('Not Available')
        else:
            li.append(webdriver_obj[i].text)
    return li

def scrape_flipkart_data(product_name):
    url = get_flipkart_url(product_name)
    service = get_chrome_service()

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        driver.set_page_load_timeout(20)

        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.k7wcnx')))
        except Exception:
            pass

        product_cards = driver.find_elements(By.CSS_SELECTOR, 'a.k7wcnx')
        data = {
            'short_desc': [],
            'features': [],
            'prices': [],
            'links': []
        }

        for card in product_cards:
            try:
                text = card.text.strip()
                if not text:
                    continue

                # Extract price from original text (before removing newlines)
                price_text = 'Not Available'
                for line in text.split('\n'):
                    if '₹' in line:
                        price_text = line.strip()
                        break
                
                # If no price found by line, search for rupee symbol in words
                if price_text == 'Not Available':
                    for part in text.split():
                        if '₹' in part:
                            price_text = part.strip()
                            break
                
                # Remove newlines for description
                description = text.replace('\n', ' ').strip()
                data['short_desc'].append(description)
                data['links'].append(card.get_attribute('href'))
                data['prices'].append(price_text)
                data['features'].append(description)
            except Exception as card_err:
                continue

        if not data['short_desc']:
            raise Exception('Failed to scrape data from Flipkart.')

        return data
    finally:
        try:
            driver.quit()
        except:
            pass
    
def get_flipkart_data(product_name):
    data = scrape_flipkart_data(product_name)

    data_list = []
    description_with_index = ''

    index = 0
    for i in range(len(data['short_desc'])):
        li = []
        li.append('Name : ' + data['short_desc'][i])
        description_with_index += f"'Flipkart Search Result {str(i)}' : {data['short_desc'][i]},\n" 
        li.append('Features : "' + data['features'][i] + '"') 
        li.append('Price : ' + data['prices'][i]) 
        li.append('Link : ' + data['links'][i])

        data_list.append(li.copy())
    
    return [description_with_index[:-2], data_list]

