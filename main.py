import asyncio
from datetime import datetime, timezone
import email.utils as eut
from utils.getNews import scrape_google_news, get_original_link, getArticle
from utils.selectNews import select_news_source
# import json
from utils.logger import setup_logger

from utils.db.db_utils import fetch_trusted_sources, fetch_categories, fetchSelectors

logger = setup_logger(__name__)


async def main():
    # if __name__ == "__main__":

    logger.info("Fetching trusted sources")
    trusted_sources = fetch_trusted_sources()
    logger.info("Fetched trusted sources")

    # # raw_articles = scrape_google_news(cat)

    logger.info("Fetching news sources")
    raw_articles = scrape_google_news()
    logger.info("News sources collected (%d articles)", len(raw_articles))

    articles_recent = []

    current_time = datetime.now(timezone.utc)
    logger.info("Fetching recent news source from trusted source")

    for art in raw_articles:
        article_time = datetime.fromtimestamp(eut.mktime_tz(
            eut.parsedate_tz(art['pub_date'])), tz=timezone.utc)

        article_time_spend = (
            current_time-article_time).total_seconds()/3600

        if article_time_spend <= 24 and art['source'] in trusted_sources:
            articles_recent.append(art)

    logger.info(
        f"[Filter] {len(articles_recent)} articles retained after filtering ")

    # for idx, art in enumerate(articles_recent):
    #     print(f"{idx+1} {art['title']}")

    # print()

    logger.info(
        "[Process] Selecting News")
    articles = select_news_source(articles_recent)
    print(len(articles))

    # print(articles)

    # for idx, art in enumerate(articles):
    #     print(f"{idx+1} {art['title']}")

    # print()

    # for art in articles:
    #     print(art)
    #     print()

    # print(final_articles)
    # print("final")
    logger.info("[Fetch] Retrieving content selectors for all sources")
    for i in articles:
        # print(f"{i['title']}: {i['source']} from {i['category']}")
        i['sel'] = fetchSelectors(i['source'])

        await getArticle(i)
    # print(i)

    # get articles from news

    # try:
    #     response = await get_original_link(art['link'])
    #     art.pop('link', None)
    #     art['link'] = response['article_url']
    #     art['news_title'] = response['page_title']
    #     filtered.append(art)
    # except Exception as e:
    #     print(e)

    #     # if filtered:
    #     #     for f in filtered:
    #     #         print(f)
    #     #         print()

    #     # if filtered:
    #     #     articles[cat['category_name']] = filtered

    #     # print(articles)
    # #         print()
    # # # print(articles)
    # # print()
    # # with open("./utils/articles.json", "w", encoding="utf-8") as f:
    # #     json.dump(articles, f, indent=4, ensure_ascii=False)
    # # filtered = process_article_clusters(articles)
    # # print(filtered)

    # titles = []
    # # for article in articles:
    # #     print(article['title'])
    # #     print(article['original_link'])
    # #     print()
    # #     titles.append(article['title'])

    # # for title in titles:
    # #     print(title)

if __name__ == "__main__":
    asyncio.run(main())
