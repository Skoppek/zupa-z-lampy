from bs4 import BeautifulSoup
import requests
import json
import re


def get_params(soup: BeautifulSoup) -> dict:
    params = {}
    param_tags = soup.select(".dictionary__param")
    for param_tag in param_tags:
        name = param_tag.select_one(
            ".dictionary__name  .dictionary__name_txt"
        ).text.lower()
        values = param_tag.select(".dictionary__value .dictionary__value_txt")
        values = [value.text for value in values]
        if name not in ["przeznaczenie"] and len(values) > 0:
            values = values[0]
        if name in ["wykonanie", "kolor"] and len(values) > 0:
            values = re.split(", |/", values.lower())
        params[name] = values

    return params


def scrap_product(url: str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html5lib")
    product = {}
    product["name"] = soup.select_one(".product_name__name").text
    product["price"] = soup.select_one(".projector_prices__price").text
    product["params"] = get_params(soup)
    return product


def get_product_links(url: str) -> list[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html5lib")
    products = soup.select(".products .product > a")
    return ["https://sollux.pl/" + product["href"] for product in products]


def get_number_of_pages(soup: BeautifulSoup) -> int:
    try:
        last_pagination = soup.select_one(".pagination__element:nth-last-child(2)")
        return int(last_pagination.text)
    except IndexError:
        print("No pagination")
        return 1


def get_product_pages(url: str) -> list[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html5lib")
    number_of_pages = get_number_of_pages(soup)

    return [url + f"?counter={num}" for num in range(number_of_pages)]


def append_to_json(data: list) -> None:
    # file_data = []

    # with open("result.json") as file:
    #     file_data = json.load(file)

    # if type(file_data) is not list:
    #     file_data = []
    # file_data = file_data + data

    with open("result.json", "w") as file:
        json.dump(data, file)


def main():
    url = "https://sollux.pl/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html5lib")
    categories = soup.select(".navbar-nav > .nav-item > .nav-link:first-child")
    for category in categories:
        print(f"Category: {category['title']}")
        if "href" in category.attrs:
            pages = get_product_pages(url + category["href"])
            for page in pages:
                result = []
                print(f"Page: {page}")
                product_links = get_product_links(page)
                for product_link in product_links:
                    try:
                        # result.append(scrap_product(product_link))
                        scrapped_product = scrap_product(product_link)
                        result.append(scrapped_product)
                    except Exception as err:
                        print(f"Unexpected {err=}, {type(err)=}")
                        print(product_link)
                append_to_json(result)
                break

    # result_json = json.dumps(result)
    # with open("result.json", "w") as file:
    #     file.write(result_json)


if __name__ == "__main__":
    main()
