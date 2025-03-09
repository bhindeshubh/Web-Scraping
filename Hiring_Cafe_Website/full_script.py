# Required Packages
# pip install selenium
# pip install playwright
# playwright install chromium
# pip install bs4
# pip isntall requests
# pip install lxml
# pip install pandas
# pip install tqdm
# pip install time

# Script to extract links from all the "View All" buttons
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from lxml import etree
import pandas as pd
from tqdm import tqdm
import time
import pickle
import os

formatted_address = ["Argentina","Australia","Bangladesh","Belgium","Brazil","Canada","China","Denmark","Egypt",
                     "Finland","France","Germany","Greece","India","Indonesia","Ireland","Israel","Italy","Japan",
                     "Malaysia","Mexico","Netherlands","New+Zealand","Nigeria","Norway","Oman","Pakistan",
                     "Philippines","Poland","Portugal","Qatar","Russia","Saudi+Arabia","Singapore","South+Korea","Spain",
                     "Sri+Lanka","Sweden","Switzerland","Taiwan","Thailand","Turkey","United+Arab+Emirates","United+Kingdom",
                     "United+States","Vietnam"] # List of relevant countries

long_name = formatted_address  # Reuse the same for long name

# Short Form names of the above countries
short_name = ["AR", "AU", "BD", "BE", "BR", "CA", "CN", "DK", "EG","FI", "FR", "DE", "GR", "IN", "ID", "IE", "IL", "IT", "JP",
    "MY", "MX", "NL", "NZ", "NG", "NO", "OM", "PK","PH", "PL", "PT", "QA", "RU", "SA", "SG", "KR", "ES","LK", "SE", "CH", "TW", "TH", "TR", "AE", "GB", "US", "VN"]

departments = [
    "Engineering", "Software+Development", "Information+Technology", "Data+and+Analytics", "Design", "Creative+and+Art+Services",
    "Project+and+Program+Management", "Product+Management", "Business+Operations", "Legal+and+Compliance", "Finance+and+Accounting", 
    "Human+Resources", "Administrative+%26+Clerical+Support",
    "Sales", "Marketing", "Communications+and+Public+Affairs", "Business+Development", 
    "Healthcare+Services+-+Advanced+Practice", "Healthcare+Services+-+Allied+Health", 
    "Healthcare+Services+-+Nursing", "Healthcare+Services+-+Pharmacy", "Healthcare+Services+-+Veterinary",
    "Education+Services", "Customer+Service", "Social+Services", "Skilled+Trades+-+Construction",
    "Skilled+Trades+-+Mechanical+and+Electrical", "Skilled+Trades+-+Manufacturing+and+Industrial", 
    "Skilled+Trades+-+Maintenance+and+Repair", "Skilled+Trades+-+General+Labor",
    "Transportation+Services", "Supply+Chain+%2F+Logistics+%2F+Procurement", "Quality+Assurance", 
    "Environment%2C+Health%2C+and+Safety", "Research+and+Development+%28R%26D%29",
    "Food+and+Beverage+Services", "Protective+Services", "Custodial+Services"
] # List of all the departments

all_links = set() # To save only unique links

# Selenium setup (Make sure you have the appropriate driver installed)
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options) # Remove options=options if you want to see the browser
for address, long, short in zip(formatted_address,long_name,short_name):
    for department in departments:
        url = f"https://hiring.cafe/?searchState=%7B%22locationSearchType%22%3A%22precise%22%2C%22selectedPlaceDetail%22%3A%7B%22formatted_address%22%3A%22{address}%22%2C%22types%22%3A%5B%22country%22%5D%2C%22place_id%22%3A%22FxY1yZQBoEtHp_8UEq7V%22%2C%22address_components%22%3A%5B%7B%22long_name%22%3A%22{long}%22%2C%22short_name%22%3A%22{short}%22%2C%22types%22%3A%5B%22country%22%5D%7D%5D%7D%2C%22higherOrderPrefs%22%3A%5B%22ANYWHERE_IN_CONTINENT%22%2C%22ANYWHERE_IN_THE_WORLD%22%5D%2C%22departments%22%3A%5B%22{department}%22%5D%7D"
        try:
            driver.get(url)
            
            # Wait for the page to load completely
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "chakra-portal")))

            scroll_increment = 1000  # Adjust as needed
            scroll_pause = 3  # Adjust for loading time

            # Infinite Scrolling Component
            while True:
                last_height = driver.execute_script("return window.scrollY + window.innerHeight")
                driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
                time.sleep(scroll_pause)
                
                new_height = driver.execute_script("return window.scrollY + window.innerHeight")
                if new_height == last_height:
                    print("Reached the end of the page. Stopping scrolling.")
                    break

            # Parse the page content
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Storing the soup element in pickle file
            with open(f"test/hiringcafe_soups/hiringcafe_{long}_{department}_soup.pkl", "wb") as file:
                pickle.dump(soup, file)

            # Extracting the href links from the "View All" button
            final_links = ['https://hiring.cafe' + a["href"] for a in soup.find_all("a", class_="text-xs font-medium hover:scale-105 transition-all duration-100 text-pink-600/50 hover:text-pink-600", href=True) if 'https://hiring.cafe' + a["href"] not in all_links]

            if final_links:
                new_links = []
                for link in tqdm(final_links):
                    link_mod = link[:link.find('searchState')]
                    new_links.append(link_mod + 'searchState=%7B%22defaultToUserLocation%22%3Afalse%7D') # Filter to get the jobs of that company from the entire world, instead of that specific country
                filename = f'test/view_all_links/hiringcafe_global_{long}_{department}_links.pkl'
                with open(filename, 'wb') as file:
                    pickle.dump(new_links, file) # Saving the links in pickle file according to filters
                print(f"All unique links saved to {filename}")
            all_links.clear() # Resetting the set to ensure only links from the current page are saved            
        except Exception as e:
            print(f"Error while loading {url}: {e}")

# Close the browser
driver.quit()

# Compile all the pickle files into a single pickle file
all_set = []
files = os.listdir('test/view_all_links')
for file in files:
    with open(f"test/view_all_links/{file}", 'rb') as f:
        all_companies = pickle.load(f)
        all_set.extend(all_companies)
    
with open('test/all_companies_set.pkl', 'wb') as file:
    pickle.dump(all_set, file)

# Script to extract "Full View" links of all the jobs on the Company page
with open('test/all_companies_set.pkl', 'rb') as file:
    hc_links = pickle.load(file)

print(f"Total Links: {len(hc_links)}")

# Playwright setup
with sync_playwright() as p:
    # Launch the browser
    browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser
    page = browser.new_page()

    for i, url in enumerate(hc_links, start=1):
        print(f'Extracting Page: {i} - {url}')
        # Open the website
        page.goto(url)

        # Wait for the page to load completely
        page.wait_for_load_state("networkidle")  # Wait until there are no more network requests

        last_height = page.evaluate("() => document.body.scrollHeight")
        while True:
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)  # Adjust timeout as needed
            new_height = page.evaluate("() => document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find all elements with the same CSS selector
        boxes = page.query_selector_all("div.relative.xl\\:z-10")

        href_links = []
        # Loop through each box
        for j, box in enumerate(boxes):
            try:
                print(f"Processing box {j + 1} of {len(boxes)}")

                # Scroll the box into view (if needed)
                box.scroll_into_view_if_needed()

                # Wait for the box to be visible and enabled
                box.wait_for_element_state("visible")
                box.wait_for_element_state("enabled")

                # Get the bounding box of the element
                bounding_box = box.bounding_box()

                # Check if the bounding box is available
                if bounding_box:
                    # Calculate the center coordinates
                    center_x = bounding_box["x"] + (bounding_box["width"] / 2)
                    center_y = bounding_box["y"] + (bounding_box["height"] / 2)
                    print(center_x, center_y)

                    # Hover over the box
                    page.mouse.move(center_x, center_y)

                    # Add a small delay to ensure the hover effect is applied
                    page.wait_for_timeout(3000)

                    # Perform the click at the center coordinates
                    page.mouse.click(center_x, center_y)

                    # Wait for the dynamic content to load (adjust the selector as needed)
                    page.wait_for_selector("button[class='rounded-lg p-2 text-black hover:bg-gray-200 flex-none outline-none']", state="visible", timeout=5000)
                    page.wait_for_selector("a[class='text-xs flex items-center space-x-2 p-1.5 hover:bg-gray-200 hover:rounded']", state="visible", timeout=2000)
                    # Extract the "Full View" link
                    full_view_link = page.query_selector("a[class='text-xs flex items-center space-x-2 p-1.5 hover:bg-gray-200 hover:rounded']")
                    if full_view_link:
                        href = full_view_link.get_attribute("href")
                        print(f"Full View Link: {href}")
                        href_links.append(href)
                        page.wait_for_timeout(1000)
                    else:
                        print("Full View link not found.")
                        break

                    # Find all buttons with the same selector
                    close_buttons = page.query_selector_all("button[class='rounded-lg p-2 text-black hover:bg-gray-200 flex-none outline-none']")
                    if len(close_buttons) >= 2:
                        # Click the close button
                        close_buttons[1].click()
                    else:
                        print("Less than 2 buttons found. Skipping.")

                    # Optional: Add a small delay to ensure the page is ready for the next interaction
                    page.wait_for_timeout(500)  # 500ms delay
                else:
                    print(f"Bounding box not available for box {j + 1}. Skipping.")
            except Exception as e:
                print(f"An error occurred with box {j + 1}: {e}")
                break  # Stop if there's an error
            
        with open(f'test/full_view_links/href_links_page_{i}.pkl', 'wb') as file:
            pickle.dump(href_links, file)
        href_links = []


        # Optional: Add a delay before closing the browser (for debugging)
        page.wait_for_timeout(3000)  # Wait 3 seconds before closing

    # Close the browser
    browser.close()

# Script to extract the final JDs from each company

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

files = [file for file in os.listdir("test/full_view_links")]

for CompanyNo in range(1,len(files)+1):
    try:
        with open(f'test/full_view_links/href_links_page_{CompanyNo}.pkl', 'rb') as file:
            links = pickle.load(file)
        print(f'Extracting Page No. {CompanyNo}')
    except FileNotFoundError:
        print(f'File href_links_page_{CompanyNo}.pkl not found. Skipping...')
        continue

    job_title = []
    company_name = []
    job_location = []
    responsibilities = []
    requirements_summary = []
    job_description = []

    session = requests.Session()

    for i, link in tqdm(enumerate(links, start=1), total=len(links)):
        try:
            for _ in range(3):  # Retry up to 3 times
                try:
                    response = session.get(link, headers=headers, timeout=5)
                    if response.status_code == 200:
                        break  # Exit retry loop if successful
                except requests.exceptions.RequestException:
                    print(f'Retrying {link}...')
                    continue
            else:
                print(f"Failed to extract {link} after retries.")
                continue


            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find("body")
            dom = etree.HTML(str(body))

            title_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[1]/div/div[2]/h2')
            job_title.append(title_element[0].text.strip() if title_element and title_element[0].text else '-')

            name_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[1]/div/div[2]/div[2]/span/text()[2]')
            company_name.append(name_element[0].strip() if name_element else '-')

            location_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[1]/div/div[2]/div[3]/span')
            job_location.append(location_element[0].text.strip() if location_element and location_element[0].text else '-')

            responsibilities_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[1]/div/div[2]/div[5]/span[2]')
            responsibilities.append(responsibilities_element[0].text.strip() if responsibilities_element and responsibilities_element[0].text else '-')

            requirements_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[1]/div/div[2]/div[6]/span[2]')
            requirements_summary.append(requirements_element[0].text.strip() if requirements_element and requirements_element[0].text else '-')

            desc_element = dom.xpath('//*[@id="__next"]/div[3]/div/div/div/div[2]/article')
            if desc_element and desc_element[0].xpath(".//text()"):
                full_description = " ".join(desc_element[0].xpath(".//text()")).strip()
                job_description.append(full_description)
            else:
                job_description.append('-')

        except requests.exceptions.RequestException as e:
            print(f'Failed to extract the page due to {e}')
            continue

    print(f'Successfully Extracted Page {CompanyNo}')

    data = pd.DataFrame({
        'Job Title': job_title,
        'Company': company_name,
        'Location': job_location,
        'Responsibilities Summary': responsibilities,
        'Requirements Summary': requirements_summary,
        'Job Description': job_description
    })
    data.to_csv(f'test/CSVs/Hiring_Cafe_Jobs_At_Company_{CompanyNo}.csv', index=False)
