import asyncio
from utils.getNews import scrape_google_news
import pandas as pd
import os


async def main():
    csv_path = "./data/news_dataset.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
    else:
        df_existing = pd.DataFrame(columns=["text", "label"])

    raw_articles = scrape_google_news()
    titles = [art['title'] for art in raw_articles]

    # Remove empty strings and duplicates
    titles = list(filter(None, titles))
    titles = list(dict.fromkeys(titles))

    df = pd.DataFrame({
        "text": titles,
        "label": [""] * len(titles)
    })

    df_combined = pd.concat([df_existing, df], ignore_index=True)
    # Remove duplicates (by title)
    df_combined = df_combined.drop_duplicates(subset="text", keep="first")

    df_combined.to_csv("./data/news_dataset.csv", index=False, quoting=1)
    print("Dataset created")

if __name__ == "__main__":
    asyncio.run(main())
