import requests

# Set parameters for Alexa Top Sites API
base_url = "https://ats.api.alexa.com/api"
action = "TopSites"
response_group = "Country"
start = 1
count = 1000
output_file = "top_1000000_websites.txt"

# Loop through each set of 1000 results and append to output file
with open(output_file, "w") as f:
    while start <= 1000000:
        # Build request URL with parameters
        url = f"{base_url}/{action}?ResponseGroup={response_group}&Start={start}&Count={count}"
        response = requests.get(url)

        # Write domain names to file
        for site in response.json()["Sites"]["Site"]:
            f.write(site["DataUrl"] + "\n")

        start += count

