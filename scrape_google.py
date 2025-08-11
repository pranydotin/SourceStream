import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import email.utils as eut


def scrape_google_news():
    url = "https://news.google.com/rss/search?q=uttarakhand+environment"
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


# scrape_google_news()


if __name__ == "__main__":
    print(datetime.now())
    title = []
    for art in scrape_google_news():
        # print(art['pub_date'])
        diff = datetime.now(
            timezone.utc)-datetime.fromtimestamp(eut.mktime_tz(eut.parsedate_tz(art['pub_date'])), tz=timezone.utc)
        # print(diff)
        hrs = diff.total_seconds()/3600
        # print(diff.total_seconds()/3600)
        if (hrs <= 48):
            print(art)
            print(art['title'])

        # print(art)
        # title.append(art['title'])

# print(title)
