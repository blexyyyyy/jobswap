import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

url = "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python+developer&txtLocation=India&sequence=1"

response = requests.get(url, headers=headers, timeout=10, verify=False)
print(f"Status: {response.status_code}")
print("\n=== HTML Preview ===")
print(response.text[:3000])

soup = BeautifulSoup(response.content, 'html.parser')

# Try different selectors
print("\n=== Looking for job listings ===")
print("Looking for li.clearfix.job-bx:")
cards = soup.find_all('li', class_='clearfix job-bx')
print(f"Found: {len(cards)}")

print("\nLooking for div with job classes:")
cards = soup.find_all('div', class_='jobTupleContainer')
print(f"Found jobTupleContainer: {len(cards)}")

print("\nLooking for any list items:")
items = soup.find_all('li')
print(f"Found li tags: {len(items)}")
if items:
    print("First few li tags:")
    for i, item in enumerate(items[:3]):
        print(f"  {i}: {item.get('class')}")

print("\nLooking for job-related divs:")
divs = soup.find_all('div')
for i, div in enumerate(divs[:10]):
    classes = div.get('class', [])
    if 'job' in str(classes).lower():
        print(f"  Div {i}: {div.get('class')}")
        print(f"  Div {i}: {div.get('class')}")
