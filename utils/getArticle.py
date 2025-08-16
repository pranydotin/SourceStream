
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import requests


def getArticle(article):
    # print(article)
    url = article['link']
    print(url)

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        print(page.title())
        browser.close()


async def get_original_link(url):

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        article_url = None

        def handle_request(request):
            nonlocal article_url
            req_url = request.url
            if request.resource_type == "document":
                req_url = request.url
                if "news.google.com" not in req_url:
                    article_url = req_url
                    page.remove_listener("request", handle_request)

        page.on("request", handle_request)

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        await browser.close()
        # print(article_url)
        return article_url
