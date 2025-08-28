import asyncio
from datetime import datetime, timezone
import email.utils as eut
from utils.getNews import scrape_google_news, get_original_link
from utils.getArticle import getArticle
import json

from utils.db.db_utils import fetch_trusted_sources, fetch_categories


async def main():
    if __name__ == "__main__":

        TRUSTED_SOURCE = fetch_trusted_sources()

        articles = {}
        currentTime = datetime.now(timezone.utc)

        categories = fetch_categories()
        # print(categories)
        for cat in categories:
            # print(cat)
            # nonlocal articles
            link = []

            for art in scrape_google_news(cat):
                article_time = datetime.fromtimestamp(eut.mktime_tz(
                    eut.parsedate_tz(art['pub_date'])), tz=timezone.utc)

                diff = currentTime-article_time
                # print(diff)
                hrs = diff.total_seconds()/3600
                # print(diff.total_seconds()/3600)
                if (hrs <= 48) and (art['source'] in TRUSTED_SOURCE):
                    try:
                        response = await get_original_link(art['link'])
                        art['original_link'] = response['article_url']
                        art['page_title'] = response['page_title']
                        link.append(art)
                    except Exception as e:
                        print(e)

            # print(link)
            # print(cat['category_name'])
            if link:
                articles[cat['category_name']] = link

            print(articles)
            print()
    # print(articles)
    print()
    with open("./utils/articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4, ensure_ascii=False)

    titles = []
    # for article in articles:
    #     print(article['title'])
    #     print(article['original_link'])
    #     print()
    #     titles.append(article['title'])

    # for title in titles:
    #     print(title)


asyncio.run(main())
