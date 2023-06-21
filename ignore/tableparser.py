from bs4 import BeautifulSoup
import json

# Read the HTML file into a string variable
with open('full_table.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Extract the table headers
headers = []
for header in soup.find_all('div', class_='header'):
    headers.append(header.text)

# Initialize empty arrays for each column
tlds = []
namecheap = []
bluehost = []
dreamhost = []
godaddy = []
domaincom = []
regru = []

# Extract data from Table Left
for row in soup.find('div', class_='table_left').find_all('div', class_='table_row'):
    cell = row.find('div', class_='table_cell')
    if cell:
        tlds.append(cell.text.strip())

# Extract data from Table Right
for row in soup.find('div', class_='table_right').find_all('div', class_='table_row'):
    cells = []
    for cell in row.find_all('div', class_='table_cell'):
        if cell.find('div', class_='n'):
            cells.append(cell.find('div', class_='n').text.strip())

    if not cells:
        continue

    namecheap.append(cells[0])
    bluehost.append(cells[1])
    dreamhost.append(cells[2])
    godaddy.append(cells[3])
    domaincom.append(cells[4])
    regru.append(cells[5])

tlds = tlds[1:]

# Print the arrays
print('TLDs:', tlds)
print('NameCheap:', namecheap)
print('BlueHost:', bluehost)
print('DreamHost:', dreamhost)
print('GoDaddy:', godaddy)
print('Domain.Com:', domaincom)
print('Reg.Ru:', regru)


# Create a dictionary from the arrays
table = {}
for i, tld in enumerate(tlds):
    table[tld] = {
        'NameCheap': namecheap[i],
        'BlueHost': bluehost[i],
        'DreamHost': dreamhost[i],
        'GoDaddy': godaddy[i],
        'Domain.Com': domaincom[i],
        'Reg.Ru': regru[i]
    }

# Convert the dictionary to JSON
table_json = json.dumps(table, indent=2)

for key in list(table_json.keys()):
    values = table_json[key]
    if all(value == '-' for value in values.values()):
        del table_json[key]

with open('table.json', 'w',encoding='utf-8') as f:
    f.write(table_json)

print(table_json)