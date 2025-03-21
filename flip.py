import requests
from bs4 import BeautifulSoup
import pandas as pd
import PriceApp

data = {"products": [], "prices": [], "ratings": []}

url = "https://www.flipkart.com/search?q="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}
products_class = "_31qSD5"


def getRequest():
    # search_input = input("Enter product name : ").replace(" ", "+")
    print("getting userInput...")
    search_input = PriceApp.product
    print("Product is : ", PriceApp.product)

    link = url + search_input

    source = requests.get(link, headers=headers)
    content = source.text
    soup = BeautifulSoup(content, "lxml")

    for a in soup.findAll("a", href=True, attrs={"class": products_class}):
        try:
            name = a.find("div", attrs={"class": "_3wU53n"})
            data["products"].append(name.text[:60])

            try:
                price = a.find("div", attrs={"class": "_1vC4OE _2rQ-NK"})
                data["prices"].append(int(price.text.replace("₹", "").replace(",", "")))
            except AttributeError:
                data["prices"].append("Not available")

            try:
                rating = a.find("div", attrs={"class": "hGSR34"})
                data["ratings"].append(rating.text)
            except AttributeError:
                data["ratings"].append("Not available")

        except AttributeError:
            continue

    df = pd.DataFrame(
        {
            "Product": data["products"],
            "Price": data["prices"],
            "Rating": data["ratings"],
        }
    )
    df.to_csv("flip.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    getRequest()
