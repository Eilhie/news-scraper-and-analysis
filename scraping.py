import requests
from bs4 import BeautifulSoup
import pandas as pd

# Fungsi untuk scraping dari Detik
def scrape_detik(query, label, pages=5):
    base_url = "https://www.detik.com/search/searchall?query={}"
    news_data = []
    for page in range(1, pages + 1):
        url = f"{base_url.format(query)}&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        articles = soup.find_all("article")
        for article in articles:
            try:
                title = article.find("h2").text.strip()
                link = article.find("a")["href"]
                media = "Detik.com"
                news_data.append({"Teks": title, "Media": media, "Label": label, "Link": link})
            except AttributeError:
                continue
    return news_data

# Fungsi untuk scraping dari CNN Indonesia
def scrape_cnn(query, label, pages=5):
    base_url = "https://www.cnnindonesia.com/search/?query={}"
    news_data = []
    for page in range(1, pages + 1):
        url = f"{base_url.format(query)}&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        articles = soup.find_all("article", class_="list")
        for article in articles:
            try:
                title = article.find("h2").text.strip()
                link = article.find("a")["href"]
                media = "CNN Indonesia"
                news_data.append({"Teks": title, "Media": media, "Label": label, "Link": link})
            except AttributeError:
                continue
    return news_data

# Scraping function for Detik
def extract_detik_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for specific content in Detik
        article_content = soup.find_all("div", class_="itp_bodycontent")
        if not article_content:
            article_content = soup.find_all("p")  # Fallback
        
        text = "\n".join([p.get_text(strip=True) for p in article_content])
        return text if text else "Teks tidak ditemukan"
    except Exception as e:
        return f"Error: {e}"

# Scraping function for CNN Indonesia
def extract_cnn_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for specific content in CNN
        article_content = soup.find_all("div", class_="detail-text")
        if not article_content:
            article_content = soup.find_all("p")  # Fallback
        
        text = "\n".join([p.get_text(strip=True) for p in article_content])
        return text if text else "Teks tidak ditemukan"
    except Exception as e:
        return f"Error: {e}"

# Function to handle multiple media sources
def extract_text_from_link(row):
    if row["Media"] == "Detik.com":
        return extract_detik_text(row["Link"])
    elif row["Media"] == "CNN Indonesia":
        return extract_cnn_text(row["Link"])
    else:
        return "Media tidak dikenali"


# Daftar kategori berita
categories = {
    "liga+inggris": "Liga Inggris",
    "liga+italia": "Liga Italia",
    "liga+spanyol": "Liga Spanyol",
    "liga+indonesia": "Liga Indonesia",
    "olahraga": "Olahraga Non Sepak Bola"
}

# Mengumpulkan data dari kedua media
all_news = []
for query, label in categories.items():
    all_news.extend(scrape_detik(query, label, pages=2))  # 2 halaman dari Detik
    all_news.extend(scrape_cnn(query, label, pages=2))   # 2 halaman dari CNN

# Simpan data ke DataFrame dan file CSV
df = pd.DataFrame(all_news)
# df.to_csv("berita_scraped.csv", index=False)

# Assuming your DataFrame is named `df`
df["Teks_Artikel"] = df.apply(extract_text_from_link, axis=1)

print(df)
df.to_csv("berita_scraped.csv", index=False)