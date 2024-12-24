import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

# Global Constants
BASE_URL = "https://abc07.ru"

CATALOG_URL = BASE_URL + "/catalog/kraski_i_lak/"
MAIN_PAGE_URL = BASE_URL
FAVORITES_PAGE_URL = BASE_URL + "/favorite/"
PRODUCT_ROW_SELECTOR = ".product-row .js-item"
PRODUCT_TITLE_SELECTOR = ".product-item_title a"
PRODUCT_PRICE_SELECTOR = ".product-item_price"
FAV_ICON_SELECTOR = ".product-item_fav"
PRODUCT_MAIN_PAGE_SELECTOR = ".product-item.js-item"
FAVORITE_PAGE_ITEM_SELECTOR = ".product-item"

PRODUCT_PAGE_TITLE_SELECTOR = ".product-card_title"
PRODUCT_PAGE_PRICE_SELECTOR = ".product-card_price"
PRODUCT_PAGE_FAV_ICON_SELECTOR = ".product-card_fav"

MAIN_PAGE_TITLE_SELECTOR = ".product-card_title"
MAIN_PAGE_PRICE_SELECTOR = ".product-card_price"
MAIN_PAGE_FAV_ICON_SELECTOR = ".product-card_fav"

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    #options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

# Helper functions
def clean_price(price):
    return ''.join(filter(str.isdigit, price))

def get_first_product_info_catalog(driver, page_url):
    driver.get(page_url)

    product = driver.find_element(By.CSS_SELECTOR, PRODUCT_ROW_SELECTOR)
    title = product.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR).text
    price = clean_price(product.find_element(By.CSS_SELECTOR, PRODUCT_PRICE_SELECTOR).text)

    return product, title, price

def get_first_product_info_main_page(driver, page_url):
    driver.get(page_url)

    products = driver.find_elements(By.CSS_SELECTOR, PRODUCT_MAIN_PAGE_SELECTOR)
    for product in products:
        title_element = product.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR)
        title = title_element.text.strip()
        if title:
            price = clean_price(product.find_element(By.CSS_SELECTOR, PRODUCT_PRICE_SELECTOR).text)
            return product, title, price

    raise ValueError("No product with a non-empty title found on the page")

def click_favorites_button(product):
    fav_icon = product.find_element(By.CSS_SELECTOR, FAV_ICON_SELECTOR)
    fav_icon.click()


def open_favorites(driver):
    driver.get(FAVORITES_PAGE_URL)

def is_product_in_favorites(driver, title, price):
    products = driver.find_elements(By.CSS_SELECTOR, PRODUCT_ROW_SELECTOR)
    for p in products:
        product_title = p.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR).text
        product_price = clean_price(p.find_element(By.CSS_SELECTOR, PRODUCT_PRICE_SELECTOR).text)
        if title.lower() == product_title.lower() and price == product_price:
            return True
    return False

def get_product_info_from_product_page(driver, product_link):
    driver.get(product_link)
    title = driver.find_element(By.CSS_SELECTOR, PRODUCT_PAGE_TITLE_SELECTOR).text
    price = clean_price(driver.find_element(By.CSS_SELECTOR, PRODUCT_PAGE_PRICE_SELECTOR).text)
    return title, price

def add_to_favorites_from_product_page(driver):
    fav_icon = driver.find_element(By.CSS_SELECTOR, PRODUCT_PAGE_FAV_ICON_SELECTOR)
    fav_icon.click()

def remove_from_favorites_from_product_page(driver):
    fav_icon = driver.find_element(By.CSS_SELECTOR, PRODUCT_PAGE_FAV_ICON_SELECTOR)
    fav_icon.click()

# Tests
@pytest.mark.parametrize("test_name", ["Добавление товара в избранное из каталога"])
def test_add_from_catalog(driver, test_name):
    # Arrange
    product, title, price = get_first_product_info_catalog(driver, CATALOG_URL)

    # Act
    click_favorites_button(product)
    open_favorites(driver)

    # Assert
    assert is_product_in_favorites(driver, title, price)

@pytest.mark.parametrize("test_name", ["Добавление товара в избранное со страницы продукта"])
def test_add_from_product_page(driver, test_name):
    # Arrange
    product, catalog_title, catalog_price = get_first_product_info_catalog(driver, CATALOG_URL)
    product_link = product.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR).get_attribute("href")

    # Act
    product_page_title, product_page_price = get_product_info_from_product_page(driver, product_link)
    add_to_favorites_from_product_page(driver)
    open_favorites(driver)

    # Assert
    assert is_product_in_favorites(driver, product_page_title, product_page_price)

@pytest.mark.parametrize("test_name", ["Добавление товара в избранное с главной страницы"])
def test_add_from_main_page(driver, test_name):
    # Arrange
    product, title, price = get_first_product_info_main_page(driver, MAIN_PAGE_URL)

    # Act
    click_favorites_button(product)
    open_favorites(driver)

    # Assert
    assert is_product_in_favorites(driver, title, price)

@pytest.mark.parametrize("test_name", ["Добавление в избранное нескольких товаров"])
def test_add_multiple_products(driver, test_name):
    # Arrange
    driver.get(CATALOG_URL)
    products = driver.find_elements(By.CSS_SELECTOR, PRODUCT_ROW_SELECTOR)[:2]

    product_data = []
    for product in products:
        title = product.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR).text
        price = clean_price(product.find_element(By.CSS_SELECTOR, PRODUCT_PRICE_SELECTOR).text)
        product_data.append({'title': title, 'price': price})

    # Act
    for product in products:
        click_favorites_button(product)
    open_favorites(driver)

    # Assert
    for data in product_data:
        assert is_product_in_favorites(driver, data['title'], data['price'])

@pytest.mark.parametrize("test_name", ["Удаление товара из избранного с каталога"])
def test_remove_from_catalog(driver, test_name):
    # Arrange
    product, title, price = get_first_product_info_catalog(driver, CATALOG_URL)
    click_favorites_button(product)
    time.sleep(3)

    # Act
    click_favorites_button(product)
    time.sleep(3)

    open_favorites(driver)

    # Assert
    assert not is_product_in_favorites(driver, title, price)

@pytest.mark.parametrize("test_name", ["Удаление товара из избранного со страницы продукта"])
def test_remove_from_product_page(driver, test_name):
    # Arrange
    product, catalog_title, catalog_price = get_first_product_info_catalog(driver, CATALOG_URL)
    product_link = product.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR).get_attribute("href")
    product_page_title, product_page_price = get_product_info_from_product_page(driver, product_link)
    add_to_favorites_from_product_page(driver)
    time.sleep(3)

    # Act
    remove_from_favorites_from_product_page(driver)
    time.sleep(3)

    open_favorites(driver)

    # Assert
    assert not is_product_in_favorites(driver, product_page_title, product_page_price)

@pytest.mark.parametrize("test_name", ["Удаление товара из избранного с главной страницы"])
def test_remove_from_main_page(driver, test_name):
    # Arrange
    product, title, price = get_first_product_info_main_page(driver, MAIN_PAGE_URL)
    click_favorites_button(product)
    time.sleep(3)

    # Act
    click_favorites_button(product)
    time.sleep(3)

    open_favorites(driver)

    # Assert
    assert not is_product_in_favorites(driver, title, price)

@pytest.mark.parametrize("test_name", ["Удаление товара из избранного со страницы избранного"])
def test_remove_from_favorites_page(driver, test_name):
    # Arrange
    product, title, price = get_first_product_info_catalog(driver, CATALOG_URL)
    click_favorites_button(product)
    time.sleep(3)

    open_favorites(driver)

    # Act
    item = driver.find_element(By.CSS_SELECTOR, FAVORITE_PAGE_ITEM_SELECTOR)
    click_favorites_button(item)
    time.sleep(3)

    # Assert
    assert not is_product_in_favorites(driver, title, price)
