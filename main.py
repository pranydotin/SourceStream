import asyncio
from datetime import datetime, timezone
import email.utils as eut
from utils.getNews import scrape_google_news, get_original_link
from utils.selectNews import process_article_clusters
import json

from utils.db.db_utils import fetch_trusted_sources, fetch_categories


async def main():
    if __name__ == "__main__":

        trusted_sources = fetch_trusted_sources()
        # categories = fetch_categories()
        current_time = datetime.now(timezone.utc)

        articles = {}

        # raw_articles = scrape_google_news(cat)
        raw_articles = scrape_google_news()
        filtered = []
        # print(raw_articles)
        for art in raw_articles:
            article_time = datetime.fromtimestamp(eut.mktime_tz(
                eut.parsedate_tz(art['pub_date'])), tz=timezone.utc)

            article_time_spend = (
                current_time-article_time).total_seconds()/3600

            if (article_time_spend <= 24) and (art['source'] in trusted_sources):

                print(art)
                print()
                # try:
                #     response = await get_original_link(art['link'])
                #     art.pop('link', None)
                #     art['link'] = response['article_url']
                #     art['news_title'] = response['page_title']
                #     filtered.append(art)
                # except Exception as e:
                #     print(e)

        if filtered:
            for f in filtered:
                print(f)
                print()

            # if filtered:
            #     articles[cat['category_name']] = filtered

            # print(articles)
    #         print()
    # # print(articles)
    # print()
    # with open("./utils/articles.json", "w", encoding="utf-8") as f:
    #     json.dump(articles, f, indent=4, ensure_ascii=False)
    # filtered = process_article_clusters(articles)
    # print(filtered)

    titles = []
    # for article in articles:
    #     print(article['title'])
    #     print(article['original_link'])
    #     print()
    #     titles.append(article['title'])

    # for title in titles:
    #     print(title)


asyncio.run(main())
