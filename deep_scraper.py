import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def deep_scrape_with_resume():
    # 1. Load the links
    input_file = "shl_individual_tests.csv"
    output_file = "shl_full_database.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found in this folder!")
        return

    df_links = pd.read_csv(input_file)
    
    # 2. Check existing progress
    full_data = []
    scraped_urls = set()
    if os.path.exists(output_file):
        df_existing = pd.read_csv(output_file)
        full_data = df_existing.to_dict(orient='records')
        scraped_urls = set(df_existing['URL'].tolist())
        print(f"Found existing file. Resuming from item {len(full_data)}...")

    # 3. Setup Browser
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Uncomment to run in background
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for index, row in df_links.iterrows():
            url = row['URL']
            if url in scraped_urls:
                continue

            try:
                driver.get(url)
                time.sleep(3) # Wait for page content
                
                # Extract Description using XPath
                try:
                    desc_xpath = "//h4[text()='Description']/following-sibling::p"
                    description = driver.find_element(By.XPATH, desc_xpath).text.strip()
                except:
                    description = "N/A"

                # Extract Test Type
                try:
                    type_row = driver.find_element(By.XPATH, "//p[contains(., 'Test Type')]")
                    test_type = type_row.text.replace("Test Type:", "").strip()
                except:
                    test_type = "A"

                full_data.append({
                    "Assessment Name": row['Assessment Name'],
                    "URL": url,
                    "Description": description,
                    "Test Type": test_type
                })

                # Save every single time an item is scraped
                pd.DataFrame(full_data).to_csv(output_file, index=False)
                print(f"{len(full_data)}/{len(df_links)}: {row['Assessment Name'][:40]}")

            except Exception as e:
                print(f"Error on {url}: {e}")
                continue
                
    finally:
        driver.quit()
        print(" Scraper finished or stopped.")

if __name__ == "__main__":
    deep_scrape_with_resume()