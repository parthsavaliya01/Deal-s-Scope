import os

from scrape_flipkart_data import get_flipkart_url
from scrape_croma_data import get_croma_api_search_url
from extract_product_name import getProductName


def test_flipkart_url():
    url = get_flipkart_url("iphone 15")
    assert "flipkart.com/search" in url


def test_croma_url():
    url = get_croma_api_search_url("iphone 15")
    assert "api.croma.com/searchservices" in url


def test_extract_product_name_local():
    os.environ["DISABLE_LLM"] = "true"
    name = getProductName("I want to buy iphone 15 256gb")
    assert "iphone" in name.lower()
