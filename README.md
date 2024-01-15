# Website-Testing-Automation
- This automated code tests the website for broken URLs (here it only check if the status is equal to 200, if any status other than 200 it will consider it as broken) and much more.
- This repository contains two automation scripts for website testing one tests only the broken parent domain URLs i.e. href links & img src links i.e. "website_testing.py" and the other one is advance version i.e. "advance_web_testing" that tests for broken URLs i.e. href links & img src links across the entire website whether it belongs to the parent domain or other domain, checks for Google Tag Manager layer, checks that iFrame works properly & Pop-up URLs open properly or not using Javascript.

**Normal Website Testing**
- This Python script utilizes Selenium WebDriver and Requests library to perform automated testing on a website. It checks for broken links, extracts href and img src links, and generates CSV files for other domain URLs and broken links.

**Features:**
- Iteratively visits links starting from a given URL.
- Checks for broken links, href links, and img src links.
- Handles read timeouts and tracks URLs with issues separately.
- Excludes URLs with '#' (fragment identifier) or 'utm_source' (tracking parameter).
- Generates CSV files for other domain URLs and broken links.

**Output:**
- All visited URLs, href links, and img src links are printed in the terminal.
- Broken href links and broken image src links are reported with their respective status codes.
- Generate two CSV files i.e. ('other_domain_urls.csv' and 'broken_links.csv') for analysis.

**Advanced Website Testing**
- This Python script extends the capabilities of normal website testing by checking for iFrames, Pop-Ups, and Google Tag Manager layer along with the basic functionalities.

**Additional Features:**
- Checks for iFrames, Pop-Ups, and Google Tag Manager layer.
- Generates CSV files for broken links, Google Tag Manager URLs, broken iFrames, broken Pop-Ups, and URLs with read timeouts.

**Output:**
- All visited URLs, href links, img src links, iFrames, Pop-Ups, and Google Tag Manager layer URLs are printed in the terminal.
- Broken href links and broken image src links are reported with their respective status codes.
- Generate CSV files i.e. ('broken_links.csv', 'google_tag_manager_urls.csv', 'broken_iframe_popup_urls.csv', and 'read_timeout_urls.csv') for further analysis.

## Usage
Install dependencies:
- pip install selenium
- pip install webdriver_manager
- pip install selenium requests


**Configuration:**
- Replace the placeholder text in the scripts with your specific details:
- Replace 'https://testurl.com' with the starting URL for both scripts.
- For the normal script, run "python website_testing.py"
- For the advanced script, run "python advance_web_testing.py"

**Notes:**
- Ensure that you have the appropriate webdriver executable installed (e.g., chromedriver for Chrome) and provide the path explicitly in the script.

**License**
- This project is licensed under the MIT License - see the LICENSE file for details.

**Acknowledgements**
- Special thanks to the developers of Selenium for providing a powerful web automation library.
- Feel free to contribute and report issues!
