import csv
import requests
from bs4 import BeautifulSoup
from langdetect import detect

# Open the CSV file
with open('domains.csv') as csvfile:
    reader = csv.reader(csvfile)
    
    # Initialize an empty list to store the domains and descriptions
    domains = []
    descriptions = []
    
    # Loop through each row in the CSV file
    for row in reader:
        # Get the domain (the second column) and send a GET request to it
        domain = row[1]
        headers = {'Accept-Language': 'en-US,en;q=0.8'}
        response = requests.get('https://' + domain, headers=headers)
        
        # Parse the HTML response with BeautifulSoup and extract the meta description
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description.get('content') if meta_description else ''
        
        # Detect the language of the description
        try:
            lang = detect(description)
        except:
            lang = ''
        
        # Filter out non-English descriptions
        if lang == 'en':
            # Add the domain and description to the lists
            domains.append(domain)
            descriptions.append(description)

# Write the domains and descriptions to a CSV file
with open('descriptions.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write the header row
    writer.writerow(['Domain', 'Description'])
    
    # Write each domain and description as a row in the CSV file
    for i in range(len(domains)):
        writer.writerow([domains[i], descriptions[i]])
