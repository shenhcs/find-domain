import whois
import os
import dns.resolver
import json

from whois.parser import PywhoisError
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from domain_generator import *
from dotenv import load_dotenv
# from llama_cpp import Llama
from pathlib import Path


load_dotenv()  # This line loads the .env file

app = Flask(__name__)
CORS(app)

# Load the JSON file containing the pricing information
with open('prices.json', 'r') as f:
    price_data = json.load(f)

# List of available extensions
extensions = [
    '.com',  # Most popular
    '.org',
    '.net',
    '.info',
    '.io',
    '.co',
    '.me',
    '.biz',
    '.us',
    '.uk',
    '.ca',
    '.au',
    '.de',
    '.fr',
    '.cn',
    '.in',
    '.br',
    '.ru',
    '.edu',
    '.gov',
    '.ai'   # Least popular (among the provided extensions)
]

# Global set to store already generated domain names
generated_domains = set()
description = ""
selectedExtensions = []


@app.route("/generate_domains_without_extensions", methods=["POST"])
def generate_domains_without_extensions_route():
    print("generate_domains_without_extensions_route")
    data = request.get_json()
    description = data["description"]
    generated_domains = data["generatedDomains"]
    num_domains = 30
    try:
        domains = generate_domains_without_extension(
            description, generated_domains, num_domains)
        return jsonify({"domains": domains})
    except ValueError as e:
        # Return a 400 Bad Request status code with an error message
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", extensions=extensions)


@app.route("/check_availability", methods=["GET"])
def check_availability():
    print("check availibility")
    domain_name = request.args.get("domain")

    if has_dns(domain_name):
        print("has dns")
        return jsonify({"available": False})

    try:
        print("does not have dns")
        w = whois.whois(domain_name)
        if w.status is None:
            return jsonify({"available": True})
        return jsonify({"available": False})
    except whois.parser.PywhoisError:
        return jsonify({"available": True})


@app.route("/get_domain_details", methods=["GET"])
def get_domain_details():
    # Get the domain name from the query parameters
    domain = request.args.get('domain')

    # Get the extension from the domain name
    # extension = '.' + domain.split('.')[-1]
    extension = domain.split('.')[-1]

    providers = []

    provider_dict = {
        'name': "NameCheap",
        'url': "https://namecheap.pxf.io/c/173116/386170/5618?u=https%3A%2F%2Fwww.namecheap.com%2Fdomains%2Fregistration%2Fresults.aspx%3Fdomain%3D"+domain,
        'price': get_price(extension, "NameCheap")
    }
    providers.append(provider_dict)
    provider_dict = {
        'name': "GoDaddy",
        'url': "https://click.godaddy.com/affiliate?isc=cjc1off30&url=https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck=domain%3D"+domain,
        'price': get_price(extension, "GoDaddy")
    }
    providers.append(provider_dict)

    # Return the JSON object
    return json.dumps(providers, indent=2)


def get_price(extension, provider):
    # Check if the extension exists in the pricing data
    if extension in price_data:
        # Check if the provider exists in the pricing data for the extension
        if provider in price_data[extension]:
            price = price_data[extension][provider]
            if price == '-':
                return "check registar"
            else:
                return price
        else:
            # If the provider doesn't exist, return an error message
            return "check registar"
    else:
        # If the extension doesn't exist, return an error message
        return "check registar"


def has_dns(domain_name):
    try:
        # query for A record
        dns.resolver.query(domain_name, 'A')
    except dns.resolver.NXDOMAIN:
        # domain does not exist
        return False
    except dns.resolver.NoAnswer:
        # domain exists, but no A record found
        return False
    except dns.exception.Timeout:
        # timeout occurred
        return False
    except dns.resolver.NoNameservers:
        return False

    return True


# def model_init():
#     models_dir = Path('models')
#     model_name = os.getenv("MODEL_NAME")
#     if model_name is None:
#         raise EnvironmentError("MODEL_NAME env not defined.")
#     model_path = models_dir / model_name
#     if not model_path.exists():
#         raise FileNotFoundError(f"Specified model '{model_path}' does not exist.\
#                                 Check the path.")
#     return Llama(model_path=model_path.as_posix())


def main():
    app.run(host="0.0.0.0", port=80, debug=True)


if __name__ == "__main__":
    # model = model_init()
    main()
