# This is an advance website testing code which go through the entire website for broken links(here it only check if the status is equal to 200, if any status other than 200 it will consider it as broken), href, img src and other URLs too.
# It will check for iFrames, Pop-Ups & Google Tag Manager layer using Selenium driver function along with Javascript.
# Just enter the testing website URL in "start_url".
# It takes a starting URL as input and iteratively visits links on the website, printing URLs, href links, img src, iFrames, Google Tag Manager layer, and Pop-Up links in the terminal window. 
# After the execution of this code, it prints all the broken links, href, and img src in a CSV file.
# The code will print all the URLs, href links, img src, iFrames, Google Tag Manager layer & Pop-Up links in terminal window while iterating through code.
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from selenium import webdriver
import requests
import time
import csv


# The Adv_Web_Testing class is designed for advanced website testing, checking for broken links, href, img src, iFrames, Pop-Ups, and Google Tag Manager layer using Selenium WebDriver functions along with JavaScript.
class Adv_Web_Testing:
    def __init__(self):
    # Initialize sets to store visited links, hrefs, img_src, and sets for broken links, Google Tag Manager URLs, iframe URLs, popup URLs, and URLs with read timeouts
        self.visited_links = set()
        self.visited_href = set()
        self.visited_img_src = set()
        self.broken_href = set()
        self.broken_img_src = set()
        self.google_tag_manager_urls = set()
        self.broken_iframe_urls = set()
        self.broken_popup_urls = set()
        self.read_timeout_urls = set()

# This function checks that URLs that're navigating by this program belongs to same domain, it doesn't navigate to other domain which doesn't belong to the parent domain:
# Example URL: "testing.com"(suppose parent domain) then all URLs i.e. test.testing.com, dev.testing.com, uat.testing.com etc..
    def is_same_domain(self, url1, url2):
        domain1 = urlparse(url1).netloc.split('.')[-2:]
        domain2 = urlparse(url2).netloc.split('.')[-2:]
        return domain1 == domain2

    # Check the status of a URL, implementing retry mechanism with exponential backoff
    def check_status(self, url, max_tries=3, timeout=5):
        try_count = 0
        backoff_time = 1

        while try_count < max_tries:
            try:
                # Send a HEAD request to the specified URL with a timeout constraint
                response = requests.head(url, timeout=timeout)
                status_code = response.status_code
                return status_code
            # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'    
            except requests.RequestException as e:
                print(f"Error checking status for {url}: {e}")
                if "Read timed out" in str(e):
                    print(f"Read timed out for {url}. Adding to read_timeout_urls set.")
                    self.read_timeout_urls.add(url)
                    return None
                try_count += 1
                if try_count < max_tries:
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponential backoff
                else:
                    print(f"Max tries reached for {url}. Skipping...")
                    return None  # Skip checking status and return None

    # Visit links iteratively starting from a given URL
    def visit_links_iteratively(self, starting_url, max_links=3000):
        stack = [(starting_url, 1)]
        links_visited = 0

        while stack and links_visited < max_links:
            url, depth = stack.pop()

            # Check if the URL belongs to the same domain
            if not self.is_same_domain(starting_url, url):
                print(f"Skipping {url} as it does not belong to the same domain.")
                continue

            # Check for other conditions before visiting
            if depth > max_links or url in self.visited_links or '#' in url or 'utm_source' in url:
                continue

            self.visited_links.add(url)
            links_visited += 1
            print(f"Visiting: {url}")

            options = Options()
            options.headless = False
            service = Service('# Replace with your path to chromedriver') 
            driver = webdriver.Chrome(service=service, options=options)

            try:
                driver.get(url)
            # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'
            except Exception as e:
                print(f"Error accessing URL: {url}. Skipping...")
                driver.quit()
                continue

            # Find all anchor elements on the page
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    # Extract href attribute from the anchor element
                    href = link.get_attribute('href')
                    
                    # Check if the href is valid and meets certain conditions
                    if href and '#' not in href and 'utm_source' not in href and href not in self.visited_href:
                        print(f"Visiting href: {href}")
                        
                        # Check the status code of the href link
                        status_code = self.check_status(href)
                        
                        # If the status code indicates a broken link, add it to the set
                        if status_code is not None and status_code != 200:
                            print(f"Broken href link found: {href} (Status code: {status_code})")
                            self.broken_href.add(href)
                            
                        # Add the href to the set of visited hrefs
                        self.visited_href.add(href)
                        
                        # Add the href to the stack for further exploration
                        stack.append((href, depth + 1))
                # Catches an exception indicating that a referenced element is no longer present in the DOM
                except StaleElementReferenceException:
                    print("Stale Element Exception occurred. Skipping this element.")
                    continue

            # Find all image elements on the page
            images = driver.find_elements(By.TAG_NAME, 'img')
            for img in images:
                try:
                    # Extract src attribute from the image element
                    img_src = img.get_attribute('src')
                    
                    # Check if the img_src is valid and has not been visited before
                    if img_src and img_src not in self.visited_img_src:
                        print(f"Visiting ImgSrc: {img_src}")
                        
                        # Check the status code of the image source
                        status_code = self.check_status(img_src)
                        
                        # If the status code indicates a broken source, add it to the set
                        if status_code is not None and status_code != 200:
                            print(f"Broken image source found: {img_src} (Status code: {status_code})")
                            self.broken_img_src.add(img_src)
                            
                        # Add the img_src to the set of visited image sources
                        self.visited_img_src.add(img_src)
                # Catches an exception indicating that a referenced element is no longer present in the DOM
                except StaleElementReferenceException:
                    print("Stale Element Exception occurred. Skipping this element.")
                    continue

            try:
                # Find all iframe elements on the page
                iframe_elements = driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe_element in iframe_elements:
                    try:
                        # Open a new blank window using JavaScript
                        popup_handles_before = driver.window_handles
                        driver.execute_script("window.open('about:blank','_blank');")
                        popup_handles_after = driver.window_handles

                        # Check if a new popup window is successfully opened
                        if len(popup_handles_after) > len(popup_handles_before) + 1:
                            print("Popup window opened successfully.")
                        else:
                            print("Error: Unable to open the popup window.")
                            self.broken_popup_urls.add(url)
                    # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'
                    except Exception as e:
                        print(f"Error while handling iframe or popup: {e}")
                        self.broken_iframe_urls.add(url)
            # Catches an exception indicating that a referenced element is no longer present in the DOM
            except StaleElementReferenceException:
                print("Stale Element Exception occurred. Skipping iframe handling.")

            try:
                # Check Google Tag Manager's dataLayer and print if present
                data_layer = driver.execute_script("return window.dataLayer;")
                if data_layer:
                    print("Google Tag Manager's dataLayer is present.")
                    self.google_tag_manager_urls.add(url)
            except StaleElementReferenceException:
                print("Stale Element Exception occurred while checking Google Tag Manager's dataLayer.")
            # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'
            except Exception as e:
                print(f"Error checking Google Tag Manager's dataLayer: {e}")

            driver.quit()

    # Generate CSV files for broken links
    def generate_csv(self):
        with open('broken_links.csv', 'w', newline='') as csvfile:
            fieldnames = ['broken_href', 'broken_img_src', 'status_code']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for href_link in self.broken_href:
                status_code = self.check_status(href_link)
                writer.writerow({'broken_href': href_link, 'broken_img_src': '', 'status_code': status_code})

            for img_src_link in self.broken_img_src:
                status_code = self.check_status(img_src_link)
                writer.writerow({'broken_href': '', 'broken_img_src': img_src_link, 'status_code': status_code})
            
        with open('google_tag_manager_urls.csv', 'w', newline='') as csvfile:
            fieldnames = ['google_tag_manager_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for url in self.google_tag_manager_urls:
                writer.writerow({'google_tag_manager_url': url})

        with open('broken_iframe_popup_urls.csv', 'w', newline='') as csvfile:
            fieldnames = ['broken_iframe_url', 'broken_popup_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for iframe_url in self.broken_iframe_urls:
                writer.writerow({'broken_iframe_url': iframe_url, 'broken_popup_url': ''})

            for popup_url in self.broken_popup_urls:
                writer.writerow({'broken_iframe_url': '', 'broken_popup_url': popup_url})

        with open('read_timeout_urls.csv', 'w', newline='') as csvfile:
            fieldnames = ['read_timeout_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for url in self.read_timeout_urls:
                writer.writerow({'read_timeout_url': url})
        
        # Print statement after CSV generation
        print("CSV files generated successfully!")  



# Initiate the Adv_Web_Testing class:
crawl_test = Adv_Web_Testing()

# Set the starting URL for testing: Replace "https://testurl.com" with webiste URL that you want to test. 
starting_url = 'https://testurl.com'

# Start the website testing:
crawl_test.visit_links_iteratively(starting_url, max_links=3000)
crawl_test.generate_csv()
