import whois
import re
import threading
import os
import requests
import json
import openai

from dotenv import load_dotenv


model_lock = threading.Lock()

load_dotenv()
#llama_api_endpoint = os.getenv("LLAMA_API_ENDPOINT")
#llama_api_key = os.getenv("LLAMA_API_KEY")
openai_api_endpoint = "https://api.openai.com/v1/chat/completions"

openai_api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_API_KEY") is None:
    raise EnvironmentError("OPENAI_API_KEY env not defined.")


# TODO: Should be a class...


def proc_txt(text):
    if "I apologize" in text:
        print(f"Inference refused. Output: {text}")
        return []

    # extract domain names
    dnlist = re.findall(r"(\w+)\.\w+", text)
    # only alphanumeric or hyphen
    dnlist = [domain for domain in dnlist if re.match(
        r"^[a-zA-Z0-9-]+$", domain)]
    return dnlist


def get_inference(description, num_domains=50):
    print("Generating domain names...")
    user_prompt = f"Generate domain names for {description}"

    sys_prompt_content = f"You are David Ogilvy of domain name generation.\
    Given a description of business idea, you can think of creative, catchy and fun domain names.\
    Always answer with a list of {num_domains} domain names without explanation."

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": sys_prompt_content},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(openai_api_endpoint, headers=headers, json=data)
    print(response.json())
    # Check the response
    if response.status_code == 200:
        completion = response.json()
        # Extract the message from the completion if needed
        return proc_txt(completion['choices'][0]['message']['content'])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return []


######### LLAMA2 + local inference code #######
    # sys_prompt = f"\
    # <s>[INST] <<SYS>>\
    #     {sys_prompt_content}\
    # <</SYS>>\
    # {user_prompt}[/INST]\
    # "

    # use_local_model = False
    # if (llama_api_key is None) or (llama_api_endpoint is None):
    #     use_local_model = True

    # if not use_local_model:
    #     try:
    #         response = requests.post(
    #             llama_api_endpoint,
    #             headers={
    #                 'accept': 'application/json',
    #                 'Content-Type': 'application/json',
    #                 'api_key': llama_api_key,
    #             },
    #             json={
    #                 "messages": [
    #                     {
    #                         "content": sys_prompt_content,
    #                         "role": "system"
    #                     },
    #                     {
    #                         "content": user_prompt,
    #                         "role": "user"
    #                     }
    #                 ]
    #             }
    #         )
    #         response.raise_for_status()  # Raise an exception for HTTP errors
    #         result = response.json()
    #         return proc_txt(result["choices"][0]["message"]["content"])

    #     except requests.RequestException:
    #         use_local_model = True

    # if use_local_model:
    #     with model_lock:
    #         result = model(sys_prompt)
    # return proc_txt(result["choices"][0]["text"])

######### LLAMA2 + local inference code #######

def generate_domains_without_extension(description, num_domains=30, max_retry=3):
    print("generate_domains_without_extension")
    num_good_domains = 10
    # Clean up the description
    description = re.sub(r"[^a-zA-Z0-9\s-]", "", description)

    retry_count = 0
    domains = []
    while retry_count < max_retry:
        generated_domains = get_inference(description, num_domains)
        print(f'Generated domains: {generated_domains}')

        if len(generated_domains) == 0:
            print("No domains generated.")
            break

        domains = list(set(domains) | set(generated_domains))

        if len(domains) >= num_good_domains:
            return domains

        retry_count += 1
        print(f"Retrying ({retry_count}/{max_retry})...")

    print(
        f"Unable to generate {num_good_domains} domains after {max_retry} retries.")
    return domains


def add_extensions(domains_without_extensions, extensions):
    domains_with_extensions = []
    for domain_without_extensions in domains_without_extensions:
        for extension in extensions:
            domain_with_extension = domain_without_extensions + extension
            domains_with_extensions.append(domain_with_extension)
    return domains_with_extensions


def check_domain_availability(domain_name):
    print("check domain availibility")
    try:
        w = whois.whois(domain_name)
        return False
    except whois.parser.PywhoisError:
        return True


def generate_available_domains(description, extensions, num_domains=1):
    print("generate available domains")
    generated_domains = set()
    available_domains = []
    while len(available_domains) < num_domains:
        domains = generate_domains_without_extension(
            description, generated_domains, num_domains -
            len(available_domains)
        )
        for domain in domains:
            if domain in generated_domains:
                continue
            generated_domains.add(domain)
            for extension in extensions:
                domain_with_extension = domain + extension
                if check_domain_availability(domain_with_extension):
                    print(f"{domain_with_extension} is available")
                    available_domains.append(domain_with_extension)
                    if len(available_domains) == num_domains:
                        break
                else:
                    print(f"{domain_with_extension} is NOT available")
            if len(available_domains) == num_domains:
                break
    return available_domains
