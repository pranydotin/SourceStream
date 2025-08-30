import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

import asyncio


def scrape_google_news():
    # url = f'https://news.google.com/rss/search?q=uttarakhand%20{cat['query']}&hl=en-IN&gl=IN&ceid=IN:en'
    url = f'https://news.google.com/rss/search?q=uttarakhand'
    # print(url)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "xml")

    articles = []
    for item in soup.find_all("item"):
        title = item.title.text
        link = item.link.text
        pub_date = item.pubDate.text
        source = item.source.text
        articles.append({"title": title, "link": link,
                        "pub_date": pub_date, "source": source})
    return articles


def getArticle(article):
    url = article['link']

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        browser.close()


async def get_original_link(url):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        article_url = None
        page_title = None

        async def handle_request(request):
            nonlocal article_url
            req_url = request.url
            if request.resource_type == "document":
                req_url = request.url
                if "news.google.com" not in req_url:
                    article_url = req_url
                    page.remove_listener("request", handle_request)

        page.on("request", handle_request)

        await page.goto(url, wait_until="load")
        await page.wait_for_timeout(5000)
        h1 = page.locator('h1').first
        page_title = (await h1.text_content()).strip()

        await browser.close()

        return {"article_url": article_url,
                "page_title": page_title}


asyncio.run(get_original_link('https://news.google.com/rss/articles/CBMi_AFBVV95cUxOVTFHUE1Sdk9aS1VZbVVrMURKVjd0cnF4Z2ZOTjd5N1M3MUNBNi1TalF0ODRJZHFBNnN0U2VmYW9NanJRT0Y4NnJWY0ZtenBwR2JCNTQxNnFsRHV6Z2NLbFpfYzlYY2hGTm5STzVGVXNaWm1Ca3FuV25MYUFNX2x1MEMtQlpQcTJZQURJMUlBRGNxbXY3MEtiY3hSdEhVQlp2ZlRqeXNmN0NKMlgwQk1ybElNMDJaZHMxSTU5SE8xaXFJOXZVUzBHRnNCeFc0TW1qQmkxTzZLTFI2dllQcHFMVUhnQ0R4Y1E0WTE3VWd3Z0tjU3NrSldqeUhGdTjSAYMCQVVfeXFMUGpEWXgzcmloUWJSNXpLNnFpb3kwcW9vZWxDaWNrekVaa3NCNlgwWm9CcjgzcFJIYS1UMFhyZ1E0SXgzdUNEV2gxYjlpYUNwdE9iOGNKcGxCOEhjdWZZS3VUTjZkeTk1UEtFdW5CZ3dRMDdLTjhJQVNsZ216RHVNUXVmMnpFREt0dFpIczQ1b0x3eGJhblJBTTl6U0tfLXc4WnZ2SERuVkVZUTh2XzRnUmhVV0c1Mm1QYWl0a0NnRkJLcXByNXpWTUxYSDNzb2E0cnU1RTlJN0NaTFBvdHBTX3FKOEFMa2ZfbzNLSFZJckJxVDZNN1pueldxTkR1ZDlKb2ZXNA?oc=5'))
