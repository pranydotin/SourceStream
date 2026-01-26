import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright, TimeoutError, Error

from readability import Document

import asyncio
from utils.logger import setup_logger

logger = setup_logger(__name__)


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


async def getArticle(article):

    print(article)
    url = article['link']
    sel = article['sel']

    logger.info(f"[SCRAPE] Fetching article content: {article['source']}")

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url, wait_until="domcontentloaded")

        try:
            await page.wait_for_url(
                lambda u: "news.google.com" not in u,
                timeout=3000
            )
        except TimeoutError:
            pass

        try:
            await page.wait_for_selector(sel, timeout=5500)
            await page.wait_for_timeout(500)

        # html = await page.content()
        # doc = Document(html)
        # clean_title = doc.title()
        # clean_content_html = doc.summary()
        # print(clean_content_html)
        # text = await page.evaluate("(sel) => document.querySelector(sel)?.textContent", sel)
            text = await page.locator(sel).inner_text()
            logger.info("[Scrape] Article content extracted")
            print(text)
        except TimeoutError:
            text = None
            logger.warning(
                f"[Scrape] Selector not found for source: {sel}")

        except Error as e:
            text = None
            logger.error(
                f"[Scrape] Failed to fetch article. Error{e}", exc_info=True)

        await browser.close()


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
