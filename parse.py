from dataclasses import dataclass

import requests

from bs4 import BeautifulSoup
from config import BASE_URL_A, BASE_URL_B, NUM_PROD_ON_ONE_PAGE


@dataclass
class Product:
    title: str
    id: int
    price: float
    image: str


def parse_single_product(product_soup: BeautifulSoup) -> Product:
    try:
        product = Product(
            title=product_soup.select_one(".product-title")["title"],
            id=int(product_soup.select_one(".product-name__wrap > span").text[5:]),
            price=float(product_soup.select_one(".ty-price-num").text.replace("\xa0", "")),
            image=product_soup.select_one("img.cm-image")["src"]
        )
        return product
    except ValueError as e:
        print(e)


def get_url(keyword: str = "Кухня") -> str:
    url = BASE_URL_A + keyword.replace(" ", "+") + BASE_URL_B
    return url


def get_products(soup: BeautifulSoup) -> [Product]:
    products = soup.select(".ty-column4")
    return [parse_single_product(product_soup) for product_soup in products]


def get_num_pages(soup: BeautifulSoup) -> int:
    num_products = int(soup.select_one(".count-product > span").text)
    num_pages = num_products // NUM_PROD_ON_ONE_PAGE
    return num_pages


def get_all_products(url: str) -> [Product]:
    page = requests.get(url=url).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    num_pages = get_num_pages(first_page_soup)

    all_products = get_products(first_page_soup)

    for page_num in range(2, num_pages + 1):
        page = requests.get(url=url, params={"page": page_num}).content
        soup = BeautifulSoup(page, "html.parser")
        all_products.extend(get_products(soup))

    return all_products


def parse(request: str) -> [Product]:
    url = get_url(request)
    return get_all_products(url)
