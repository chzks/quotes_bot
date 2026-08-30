import requests
from bs4 import BeautifulSoup

def parse_quotes(url: str) -> list[dict]:
    quotes = []
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text
        tags_block = quote.find("div", class_="tags")
        tags = [tag.text for tag in tags_block.find_all("a", class_="tag")]
        quotes.append({"text": text, "author": author, "tags": tags})

    return quotes