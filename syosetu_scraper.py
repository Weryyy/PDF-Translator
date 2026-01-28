import requests
from bs4 import BeautifulSoup
import time
import os
import re

def get_total_chapters(novel_id):
    url = f"https://ncode.syosetu.com/{novel_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        # Syosetu typically has links like /n9669bk/1/, /n9669bk/2/...
        links = soup.find_all("a", href=re.compile(rf"^/{novel_id}/\d+/$"))
        if not links: return 0
        chapters = [int(re.search(r"/(\d+)/$", l["href"]).group(1)) for l in links]
        return max(chapters)
    except:
        return 500 # Fallback high number

def scrape_syosetu(novel_id, start_chapter=1, end_chapter=None):
    if end_chapter is None:
        end_chapter = get_total_chapters(novel_id)
        print(f"Detected {end_chapter} chapters for novel {novel_id}")

    base_url = f"https://ncode.syosetu.com/{novel_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    os.makedirs(f"novels/{novel_id}", exist_ok=True)
    
    print(f"Scraping novel {novel_id} chapters {start_chapter} to {end_chapter}...")

    for i in range(start_chapter, end_chapter + 1):
        chapter_url = f"{base_url}{i}/"
        try:
            response = requests.get(chapter_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch chapter {i}. Status: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Title - try new class and old class
            title = soup.find("h1", class_="p-novel__title") or soup.find("p", class_="novel_subtitle")
            title_text = title.text.strip() if title else f"Chapter {i}"
            
            # Content - try new class and old class
            content = soup.find("div", class_="p-novel__body") or soup.find("div", id="novel_honbun")
            if not content:
                print(f"Could not find content for chapter {i}")
                continue
            
            # Clean up the Japanese text (remove ruby text etc if any)
            text = content.text.strip()
            
            file_path = f"novels/{novel_id}/chapter_{i:03d}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"TITLE: {title_text}\n\n")
                f.write(text)
            
            print(f"Saved {file_path}")
            
            # Sleep to be polite to the server
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping chapter {i}: {e}")

if __name__ == "__main__":
    # Mushoku Tensei ID: n9669bk
    # Scrape entire novel (None means it will detect total)
    scrape_syosetu("n9669bk", start_chapter=1, end_chapter=None)
