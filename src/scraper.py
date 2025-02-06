from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re
import pandas as pd

# User-defined search query
query = input("Enter the product you want to search for: ").strip()

# Clean query for CSV file name
file_name = re.sub(r'[^\w\s]', '', query).replace(" ", "_")
csv_filename = f"Amazon_Scraping/{file_name}_data.csv"

# Convert query for URL format
query_url = query.replace(" ", "+")

# Set up WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

driver = setup_driver()

# Navigate to Amazon search page
url = f"https://www.amazon.in/s?k={query_url}"
driver.get(url)

# Wait for page to load
time.sleep(5)

try:
    # Check if there's a redirect page
    link_xpath = "/html/body/center/p[2]/font/b/a"
    link_element = driver.find_element(By.XPATH, link_xpath)
    
    if link_element:
        print("Redirect page detected. Clicking the link...")
        link_element.click()
        time.sleep(3)  # Wait for page reload
        driver.get(url)
        time.sleep(5)

except (NoSuchElementException, TimeoutException):
    print("No redirect page found. Proceeding with normal scraping...")

# Find all product containers
products = driver.find_elements(By.CLASS_NAME, "puis-card-container")

# Extract product details
data = {'Title': [], 'Price': []}

for product in products:
    try:
        # Extract product title
        title_tag = product.find_element(By.TAG_NAME, 'h2')
        product_title = title_tag.text.strip() if title_tag else "N/A"

        # Extract price
        try:
            price_tag = product.find_element(By.CLASS_NAME, 'a-price-whole')
            price = f"${price_tag.text.strip()}" if price_tag else "N/A"
        except NoSuchElementException:
            price = "N/A"

        # Append data to dictionary
        data['Title'].append(product_title)
        data['Price'].append(price)

    except Exception as e:
        print(f"Error processing a product: {e}")

# Close the browser
driver.quit()

# Save extracted data to CSV
df = pd.DataFrame(data)
df.to_csv(csv_filename, index=False)

print(f"Data saved to CSV: {csv_filename}")

