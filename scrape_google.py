import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import email.utils as eut


TRUSTED_SOURCE = ['Deccan Herald', 'Times of India', 'The Hindu',
                  'Tribune India', 'Hindustan Times', 'Mint', 'Press Trust of India', 'Telegraph India', 'ThePrint', 'Moneycontrol', 'Newslaundry']


def scrape_google_news():
    url = "https://news.google.com/rss/search?q=uttarakhand"
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


if __name__ == "__main__":
    print(datetime.now())
    title = []
    currentTime = datetime.now(timezone.utc)
    for art in scrape_google_news():
        article_time = datetime.fromtimestamp(eut.mktime_tz(
            eut.parsedate_tz(art['pub_date'])), tz=timezone.utc)
        diff = currentTime-article_time
        # print(diff)
        hrs = diff.total_seconds()/3600
        # print(diff.total_seconds()/3600)
        if (hrs <= 48) and (art['source'] in TRUSTED_SOURCE):
            print(art)
            print(art['title'])
            print(art['pub_date'])
            print(art['source'])
            print()

        # print(art)
        # print(art['title'])
        # print()
        # title.append(art['title'])

# print(title)
