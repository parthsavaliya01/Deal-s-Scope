import requests
import os

# get_croma_api_search_url(product_name) will give api url that contains data of search results of given product.
def get_croma_api_search_url(product_name):
  base_url = 'https://api.croma.com/searchservices/v1/search?currentPage=0&query='
  search_query = product_name.replace(" ", "%20")
  end_text = '%3Arelevance&fields=FULL&channel=WEB&channelCode=400049&spellOpt=DEFAULT'
  return base_url + search_query + end_text

# scrape croma data and return object.
def scrape_croma_data(API_URL):
  try:
    response = requests.get(API_URL, timeout=10)
    if response.status_code == 200:
      return response.json()
    else:
      raise Exception(f'Failed to get response from Croma API (Status: {response.status_code})')
  except requests.exceptions.Timeout:
    raise Exception('Croma API request timed out')
  except requests.exceptions.ConnectionError:
    raise Exception('Failed to connect to Croma API')
  except Exception as e:
    raise Exception(f'Croma API error: {str(e)}')

# prepare data in well format.
def clean_features(features):
  features = features.replace('<ul>', '')
  features = features.replace('</ul>', '')
  features = features.replace('<li>', '')
  features = features.replace('</li>', '\n')
  return features[:-2]

def prepare_croma_data(doc):
  data = []
  description_with_index = ''

  if 'products' not in doc or not doc['products']:
    raise Exception('No products found on Croma')

  for i in range(len(doc['products'])):
    try:
      product = doc['products'][i]
      li = []
      
      name = product.get('name', 'Unknown Product')
      li.append('Name : ' + name)
      description_with_index += f"'Croma Search Result {str(i)}' : {name},\n"
      
      features = product.get('quickViewDesc', 'No features available')
      li.append('Features : "' + clean_features(features) + '"')
      
      price = product.get('price', {}).get('formattedValue', 'Not Available')
      li.append('Price : ' + price)
      
      url = product.get('url', '')
      link = 'https://www.croma.com' + url if url else 'Link not available'
      li.append('Link : ' + link)

      data.append(li.copy())
    except Exception as product_err:
      continue

  if not data:
    raise Exception('Failed to parse Croma data')

  return [description_with_index[:-2], data]


def get_croma_data(product_name):
  API_URL = get_croma_api_search_url(product_name)
  doc = scrape_croma_data(API_URL)
  
  return prepare_croma_data(doc)
