import tldextract


def get_main_domain(url):
    extracted = tldextract.extract(url)
    main_domain = f"{extracted.domain}.{extracted.suffix}"
    return main_domain
