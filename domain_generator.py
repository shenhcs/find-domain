import openai
import whois
import re

openai.api_key = "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"
model_engine = "text-davinci-003"

def generate_domains_without_extension(description, generated_domains, num_domains=100, max_retry=10):
    print("generate domains without extensions")
    # Clean up the description
    description = re.sub(r'[^a-zA-Z0-9\s-]', '', description)

    # expand the website description
    prompt = f"given the following website description, describe what the website should do: '{description}'"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        stop=None,
        temperature=0.5,
        n=1
    )
    expanded_description = response.choices[0].text.strip()
    print("expanded_description", expanded_description)

    generated_domains_text = " ".join(generated_domains)
    prompt = f"generate {num_domains} domain name ideas in different styles( compound names, misspelled names, short and catchy names and abstract names etc.) without extensions for this website description:  '{expanded_description}'.\n\nDo not include any extensions. So no .com .net etc.\nDo not include these already generated domains: {generated_domains_text}\nShorter domains are prefered.\n"

    #prompt = f"give me {num_domains} domain name ideas without extensions for this website description:  '{description}'.\n\nDo not include any extensions. So no .com .net etc.\nDo not include these already generated domains: {generated_domains_text}\nShorter domains are prefered.\n"

    print("prompt", prompt)
    # Generate domain names using OpenAI's GPT-3 model
    retry_count = 0
    while retry_count < max_retry:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            stop=None,
            temperature=0.5,
            n=1
        )

        print("response", response)
        # Extract the domain names from the response
        domain_names_text = response.choices[0].text.strip()
        domains = domain_names_text.split("\n")

        # remove white spaces
        domains = [domain.strip() for domain in domains if domain.strip()]
        # remove number
        domains = [re.sub(r'^\d+\.\s*', '', domain).strip() for domain in domains]
        # removes extensions
        domains = [re.sub(r'\.[a-zA-Z]{2,}', '', domain) for domain in domains]
        # removes duplicates
        domains = list(set(domains))
        # removes it if it is in generated_domains
        domains = [domain for domain in domains if domain not in generated_domains]

        # Filter domains based on regex and exclusion from the generated_domains list
        domains = [domain.lower() for domain in domains if re.match(r'^[a-zA-Z0-9-]+$', domain) and domain not in generated_domains]

        if len(domains) >= 10:
            return domains
        else:
            retry_count += 1
            print(f"Retrying ({retry_count}/{max_retry})...")

    print(f"Unable to generate {10} domains after {max_retry} retries.")
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
        domains = generate_domains_without_extension(description, generated_domains, num_domains - len(available_domains))
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