import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_shl_catalog():
    print("Initializing browser...")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) 
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = "https://www.shl.com/solutions/products/product-catalog/"
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        print("Attempting to find 'Individual Test Solutions'...")
        time.sleep(5) 
        
        try:
            filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Individual Test')]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", filter_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", filter_button)
            print("Successfully clicked the Individual Tests tab.")
        except:
            print("Filter tab click issue, proceeding...")

        all_data = []
        page = 1
        last_first_item = "" 

        while True:
            print(f"Scraping Page {page}...")
            
        
            try:
                individual_table = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'Individual Test Solutions')]/ancestor::table")))
                rows = individual_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                
                
                if rows:
                    current_first_item = rows[0].text.strip()
                    if current_first_item == last_first_item:
                        print("Waiting for content to refresh...")
                        time.sleep(2)
                        rows = individual_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    last_first_item = rows[0].text.strip()
            except:
                print("Table not found. Ending.")
                break

            # 2. Extract Data
            for row in rows:
                try:
                    links = row.find_elements(By.TAG_NAME, "a")
                    if not links: continue
                    name = links[0].text.strip()
                    href = links[0].get_attribute("href")
                    if name and href and "/view/" in href:
                        all_data.append({"Assessment Name": name, "URL": href})
                except:
                    continue 

            # 3. Pagination - ONLY use the bottom pagination container
            try:
                pagination_containers = driver.find_elements(By.CLASS_NAME, "pagination")
                # The individual tests pagination is the last one on the page
                bottom_pagination = pagination_containers[-1] 
                
                next_btn = bottom_pagination.find_element(By.XPATH, ".//a[contains(text(), 'Next')]")
                
                # Check if 'Next' is disabled
                if "disabled" in next_btn.get_attribute("class"):
                    print("Reached the final page of Individual Tests.")
                    break
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                
                page += 1
                time.sleep(4) # Wait for Ajax to load new content
            except Exception as e:
                print(f"Pagination ended at page {page}.")
                break

        # 4. Save
        df = pd.DataFrame(all_data).drop_duplicates()
        df.to_csv("shl_individual_tests.csv", index=False)
        print(f"Finished! Total Individual Tests scraped: {len(df)}")

    except Exception as e:
        print(f"A crash occurred: {e}")
    finally:
        print("Note: Browser kept open for inspection.")

if __name__ == "__main__":
    scrape_shl_catalog()