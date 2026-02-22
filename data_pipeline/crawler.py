import asyncio
import os
import sys
import json
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cpp_engine')))
import url_engine

DATASET_DIR = "../dataset"
SCREENSHOT_DIR = os.path.join(DATASET_DIR, "screenshots")
HTML_DIR = os.path.join(DATASET_DIR, "html")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

metadata = []
engine = url_engine.FeatureExtractor()

async def fetch_and_process(url: str, label: int, index: int, context, sem: asyncio.Semaphore):
    async with sem: 
        page = await context.new_page()
        try:
            print(f"[*] Fetching ({'Phishing' if label==1 else 'Legit'}): {url}")
            
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            
            features_map = engine.extract_url_features(url)
            features_list = [features_map.get("length", 0.0), features_map.get("entropy", 0.0)] 
            
           
            screenshot_name = f"{label}_{index}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)
            await page.screenshot(path=screenshot_path)
            
            metadata.append({
                "url": url,
                "label": label,
                "screenshot_file": screenshot_name,
                "features": features_list
            })
            print(f"[+] Success: {url}")
        except Exception as e:
            
            print(f"[-] Failed: {url} | Error: {str(e)[:50]}...")
        finally:
            await page.close()

async def main():
    print("[*] Loading CSV datasets...")
    try:
        
        phish_df = pd.read_csv("verified_online.csv").head(50) 
        legit_df = pd.read_csv("top-1m.csv", names=["rank", "url"]).head(50)
        
        
        legit_df['url'] = "http://" + legit_df['url']
    except FileNotFoundError:
        print("[-] HATA: CSV dosyaları bulunamadı! 'online-valid.csv' ve 'top-1m.csv' dosyalarını data_pipeline klasörüne kopyala.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
       
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        
        # Looking at 5 simultaneous pages to avoid overwhelming the system (especially important for phishing sites that may have heavy loads or timeouts)
        sem = asyncio.Semaphore(5)
        tasks = []
        
        # Phishing (Label = 1) 
        for idx, row in phish_df.iterrows():
            tasks.append(fetch_and_process(row['url'], 1, idx, context, sem))
            
        # Legit (Label = 0) save
        # tasks
        for idx, row in legit_df.iterrows():
            tasks.append(fetch_and_process(row['url'], 0, idx, context, sem))
            
        print(f"[*] Starting concurrent scraping for {len(tasks)} URLs...")
        await asyncio.gather(*tasks) # Start all tasks concurrently
        await browser.close()
        
    # 4. Save Metadata to JSON
    metadata_path = os.path.join(DATASET_DIR, "train_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)
    print(f"[+] Dataset completely built! Metadata saved to {metadata_path}")

if __name__ == "__main__":
    asyncio.run(main())