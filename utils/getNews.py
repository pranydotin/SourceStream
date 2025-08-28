import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


def scrape_google_news(cat):
    url = f'https://news.google.com/rss/search?q=uttarakhand+({cat['query']})&hl=en-IN&gl=IN&ceid=IN:en'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "xml")

    articles = []
    for item in soup.find_all("item"):
        # print(item)
        title = item.title.text
        link = item.link.text
        pub_date = item.pubDate.text
        source = item.source.text
        articles.append({"title": title, "link": link,
                        "pub_date": pub_date, "source": source})
    return articles


def getArticle(article):
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
        print(article_url)
        print(page_title)
        return {"article_url": article_url,
                "page_title": page_title}
