import requests
from bs4 import BeautifulSoup

def get_meta_description(domain):
    # Construct the URL and send a GET request to the server
    url = "https://www." + domain
    response = requests.get(url)

    # Check the response status code and exit if it's an error
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None

    # Use BeautifulSoup to parse the HTML and extract the meta description
    soup = BeautifulSoup(response.content, "html.parser")
    meta_description = soup.find("meta", attrs={"name": "description"})
    if meta_description:
        return meta_description.get("content")
    else:
        return None



def get_top_websites():
    url = 'https://www.alexa.com/topsites'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    website_list = []
    for website in soup.select('div.tr.site-listing > div.DescriptionCell > p > a'):
        website_list.append(website.text)
    return website_list[:1000000]

print(get_meta_description("google.com"))  # Prints "Search the world's information, including webpages, images, videos and more."

get_top_websites()