import csv

# Open the CSV file
with open('domains.csv') as csvfile:
    reader = csv.reader(csvfile)
    
    # Initialize an empty list to store the domains
    domains = []
    
    # Loop through each row in the CSV file
    for row in reader:
        # Add the domain (the second column) to the list
        domains.append(row[1])

# Write the domains to a text file
with open('domains.txt', 'w') as outfile:
    outfile.write('\n'.join(domains))
