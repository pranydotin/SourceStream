import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

from readability import Document

import asyncio


def scrape_google_news():
    # url = f'https://news.google.com/rss/search?q=uttarakhand%20{cat['query']}&hl=en-IN&gl=IN&ceid=IN:en'
    url = f'https://news.google.com/rss/search?q=uttarakhand'
    # print(url)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "xml")

    articles = []
    for item in soup.find_all("item"):
        title = None
        desc = item.description.text
        inner_soup = BeautifulSoup(desc, "html.parser")
        a_tag = inner_soup.find('a')
        if a_tag:
            title = a_tag.text.strip()

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
    # async with async_playwright() as p:
    p = await async_playwright().start()
    browser = await p.firefox.launch(headless=False)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    # print(url)

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
    # await page.wait_for_timeout(5000)
    try:
        await page.wait_for_selector("h1, h2", timeout=10000)
    except:
        print("No h1 or h2 appeared within 10 seconds. Closing browser.")
        await browser.close()
        return

    h1 = page.locator('h1').first
    h2 = page.locator("h2").first
    page_title = None
    if await h1.count() > 0:
        page_title = (await h1.text_content()).strip()
    elif await h2.count() > 0:
        page_title = (await h2.text_content()).strip()

    print(page_title)

    await browser.close()

    return {"article_url": article_url,
            "page_title": page_title}

# *******************************************************************


async def fetch_article_content(url: str):
    # async with async_playwright() as p:
    p = await async_playwright().start()
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
    # await page.wait_for_timeout(5000)

    h1 = page.locator('h1').first
    page_title = (await h1.text_content()).strip()
    print(page_title)

    final_title = await page.title()
    html = await page.content()
    doc = Document(html)
    clean_title = doc.title()
    clean_content_html = doc.summary()

    print(clean_title)
    print(clean_content_html)
    soup = BeautifulSoup(clean_content_html, 'html.parser')
    print(soup)

    for i in soup.find_all('div.articlebodycontent p'):
        print(i)

    input("Press Enter to close browser...")
    await browser.close()

    return {"article_url": article_url,
            "page_title": page_title}
