import pandas as pd
import re
from collections import defaultdict
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
import time

def can_scrape(url):
    """Check robots.txt to see if scraping is allowed."""
    robots_url = urljoin(url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return False

def scrape_post_urls(url):
    """Scrape and return all <a> tags from the div with id 'consnav' EXCEPT those inside spans,
    and download the XLS file from the sidebar if available, from the given URL if allowed.
    """
    if not can_scrape(url):
        print("Scraping is not allowed by robots.txt")
        return []

    headers = {"User-Agent": "Mozilla/5.0 (compatible; SafeScraper/1.0)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    post_contents = []

    consnav_div = soup.find("div", id="consnav")
    if consnav_div:
        links = []
        for a_tag in consnav_div.find_all("a", href=True):
            if not a_tag.find_parent("span"):
                links.append(a_tag["href"])
        post_contents.append({"links": links})
    else:
        print("Div with id='consnav' not found on the page.")

    # Download XLS file from sidebar (comments)
    # sidebar_div = soup.find("div", id="sidebar")
    # if sidebar_div:
    #     sidespot_divs = sidebar_div.find_all("div", class_="sidespot")
    #     for sidespot_div in sidespot_divs:
    #         export_span = sidespot_div.find("span", class_="export")
    #         if export_span:
    #             link_tag = export_span.find("a", href=True)
    #             if link_tag:
    #                 xls_link = link_tag["href"]
    #                 filename_to_save = "comments.xls"
    #                 try:
    #                     response = requests.get(xls_link, stream=True)
    #                     response.raise_for_status()
    #
    #                     with open(filename_to_save, "wb") as f:
    #                         for chunk in response.iter_content(chunk_size=8192):
    #                             f.write(chunk)
    #
    #                     print(f"XLS file downloaded successfully and saved as {filename_to_save}")
    #                     return post_contents
    #                 except requests.RequestException as e:
    #                     print(f"Failed to download XLS file: {e}")
    #             else:
    #                 print("XLS download link not found in export span.")
    #             break
    #     else:
    #         print("Span with class='export' not found in any sidespot div.")
    # else:
    #     print("Div with id='sidebar' not found on the page.")

    return post_contents

def scrape_post_content(url):
    """Scrape and return content from <div>.post_content and <h3> from <div>.post clearfix."""
    if not can_scrape(url):
        print("Scraping is not allowed by robots.txt")
        return [], []

    headers = {"User-Agent": "Mozilla/5.0 (compatible; SafeScraper/1.0)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    post_contents = [div.get_text() for div in soup.find_all("div", class_="post_content")]

    post_titles = []
    post_clearfix_divs = soup.find_all("div", class_="post clearfix")
    for post_div in post_clearfix_divs:
        h3_tag = post_div.find("h3")
        if h3_tag:
            post_titles.append(h3_tag.get_text())

    return post_contents, post_titles

