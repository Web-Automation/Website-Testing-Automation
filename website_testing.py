# Use this code to run the entire website for broken links, href, img src and other URLs too.
# Just enter the testing website URL in "start_url":
# The code will print all the URLs, href links & img src in terminal window while iterating through code.
# After the execution of this code all the broken links, href, img src will print in the terminal as well.
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from selenium import webdriver
import requests
import time
import csv


# Web_Testing class is responsible for crawling a website, checking for broken links, extracting href and img src links, and generating CSV files for other domain URLs and broken links.
class Web_Testing:
    def __init__(self):
        # Initialize sets to store visited links, hrefs, img_src, other domain URLs, and broken links
        self.visited_links = set()
        self.visited_href = set()
        self.visited_img_src = set()
        self.other_domain_urls = set()
        self.broken_href = set()
        self.broken_img_src = set()

    # This function checks that URLs that're navigating by this program belongs to same domain, it doesn't navigate to other domain which doesn't belong to the parent domain:
    def is_same_domain(self, url1, url2):
        domain1 = urlparse(url1).netloc.split('.')[-2:]
        domain2 = urlparse(url2).netloc.split('.')[-2:]
        return domain1 == domain2

    # Check the status of a URL, implementing retry mechanism with exponential backoff
    def check_status(self, url, max_tries=3, timeout=10):
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

# Continue to the next iteration if any of these conditions are met:
# Depth exceeds the maximum allowed links (`max_links`), URL is already visited, URL contains a '#' (fragment identifier) or 'utm_source' (tracking parameter).
        while stack and links_visited < max_links:
            url, depth = stack.pop()
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

            # Extract href links
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and self.is_same_domain(url, href) and '#' not in href and 'utm_source' not in href and href not in self.visited_href:
                        print(f"Visiting href: {href}")

                        try:
                            status_code = self.check_status(href)
                            if status_code is not None and status_code != 200:
                                print(f"Broken href link found: {href} (Status code: {status_code})")
                                self.broken_href.add(href)
                        # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'
                        except requests.RequestException as e:
                            print(f"Error checking status for href link {href}: {e}. Skipping...")

                        self.visited_href.add(href)
                        stack.append((href, depth + 1))
                    elif href and not self.is_same_domain(starting_url, href):
                        self.other_domain_urls.add(href)
                # Catches an exception indicating that a referenced element is no longer present in the DOM
                except StaleElementReferenceException:
                    print("Stale Element Exception occurred. Skipping this element.")
                    continue

            # Extract img src links
            images = driver.find_elements(By.TAG_NAME, 'img')
            for img in images:
                try:
                    img_src = img.get_attribute('src')
                    if img_src and self.is_same_domain(url, img_src) and img_src not in self.visited_img_src:
                        print(f"Visiting ImgSrc: {img_src}")

                        try:
                            status_code = self.check_status(img_src)
                            if status_code is not None and status_code != 200:
                                print(f"Broken image source found: {img_src} (Status code: {status_code})")
                                self.broken_img_src.add(img_src)
                        # Catches an exception related to HTTP requests, providing access to the error details through the variable 'e'
                        except requests.RequestException as e:
                            print(f"Error checking status for image source {img_src}: {e}. Skipping...")

                        self.visited_img_src.add(img_src)
                    elif img_src and not self.is_same_domain(starting_url, img_src):
                        self.other_domain_urls.add(img_src)
                # Catches an exception indicating that a referenced element is no longer present in the DOM
                except StaleElementReferenceException:
                    print("Stale Element Exception occurred. Skipping this element.")
                    continue

            driver.quit()

  
    # Generate CSV files for other domain URLs and broken links
    def generate_csv(self):
        with open('other_domain_urls.csv', 'w', newline='') as csvfile:
            fieldnames = ['other_domain_href', 'other_domain_img']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for href_url in self.other_domain_urls:
                if href_url.startswith('http'):
                    writer.writerow({'other_domain_href': href_url, 'other_domain_img': ''})
                else:
                    writer.writerow({'other_domain_href': '', 'other_domain_img': href_url})

        with open('broken_links.csv', 'w', newline='') as csvfile:
            fieldnames = ['broken_href', 'broken_img_src', 'status_code']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for href_link in self.broken_href:
                try:
                    status_code = self.check_status(href_link)
                    writer.writerow({'broken_href': href_link, 'broken_img_src': '', 'status_code': status_code})
                except requests.RequestException as e:
                    print(f"Error checking status for broken href link {href_link}: {e}. Skipping...")

            for img_src_link in self.broken_img_src:
                try:
                    status_code = self.check_status(img_src_link)
                    writer.writerow({'broken_href': '', 'broken_img_src': img_src_link, 'status_code': status_code})
                except requests.RequestException as e:
                    print(f"Error checking status for broken image source {img_src_link}: {e}. Skipping...")

        # Print statement after CSV generation
        print("CSV files generated successfully!")  


# Initiate the Web_Testing class
crawl_test = Web_Testing()

# Set the starting URL for testing: Replace "https://testurl.com" with webiste URL that you want to test. 
starting_url = 'https://testurl.com'

# Start the website testing
crawl_test.visit_links_iteratively(starting_url, max_links=3000)
crawl_test.generate_csv()
