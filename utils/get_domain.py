import tldextract


def get_main_domain(url, return_domain_only=False):
    extracted = tldextract.extract(url)
    if return_domain_only:
        return extracted.domain
    main_domain = f"{extracted.domain}.{extracted.suffix}"
    return main_domain
