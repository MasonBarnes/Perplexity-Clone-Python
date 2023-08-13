from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
from readability import Document
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import openai
import ujson

COMPLETION_MODEL = "gpt-3.5-turbo"
SOURCE_COUNT = 5

def generate_search_query(text: str, model="gpt-3.5-turbo") -> str:
    """
    Uses OpenAI's ChatCompletions to generate a search query from a given text.

    ### Example:
    For the text `What is the new Discord username system?`, a search query similar to `discord new username system` would be generated.
    """
    return openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Given a query, respond with the Google search query that would best help to answer the query. Don't use search operators. Respond with only the Google query and nothing else."},
            {"role": "user", "content": text}
        ]
    )["choices"][0]["message"]["content"]

def get_google_search_links(query: str, source_count: int = SOURCE_COUNT) -> list[str]:
    """
    Scrapes the official Google search page using the `requests` module and returns the first `source_count` links.
    """
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    link_tags = soup.find_all("a")
    
    links = []
    for link in link_tags:
        href = link.get("href")
        if href and href.startswith("/url?q="):
            cleaned_href = parse_qs(href)["/url?q"][0]
            if cleaned_href not in links:
                links.append(cleaned_href)

    filtered_links = []
    for link in links:
        domain = urlparse(link).hostname
        exclude_list = ["google", "facebook", "twitter", "instagram", "youtube", "tiktok"]
        if not any(site in domain for site in exclude_list):
            if any(new_url.hostname == domain for new_url in [urlparse(l) for l in filtered_links]) == False:
                filtered_links.append(link)
    
    return filtered_links[:source_count]

def scrape_text_from_links(links: list) -> list[dict]:   
    """
    Uses a `ThreadPoolExecutor` to run `scrape_text_from_links` on each link in `links` concurrently, allowing for lightning-fast scraping.
    """ 
    with ThreadPoolExecutor(max_workers=len(links)) as executor:
        results = list(executor.map(scrape_text_from_link, links))
    
    for i, result in enumerate(results, start=1):
        result["result_number"] = i

    return results
    
def scrape_text_from_link(link: str) -> dict:
    """
    Uses the `requests` module to scrape the text from a given link, and then uses the `readability-lxml` module along with `BeautifulSoup4` to parse the text into a readable format.
    """
    response = requests.get(link)
    doc = Document(response.text)
    parsed = doc.summary()
    soup = BeautifulSoup(parsed, "html.parser")
    source_text = soup.get_text()
    return {"url": link, "text": summarize_text(source_text[:50000])}

def summarize_text(text: str, model="gpt-3.5-turbo-16k") -> str:
    """
    Uses OpenAI's ChatCompletions to summarize a given text.
    """
    return openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Given text, respond with the summarized text (no more than 100 words) and nothing else."},
            {"role": "user", "content": text}
        ]
    )["choices"][0]["message"]["content"]

def search(query) -> tuple[list[str], list[dict]]:
    """
    This function takes a query as input, gets top Google search links for the query, and then scrapes the text from the links.
    It returns a tuple containing the list of links and a list of dictionaries. Each dictionary contains the URL and the summarized text from the link.
    """
    links = get_google_search_links(query)
    sources = scrape_text_from_links(links)

    return links, sources

def perplexity_clone(query: str, verbose=False) -> str:
    """
    A clone of Perplexity AI's "Search" feature. This function takes a query as input and returns Markdown formatted text containing a response to the query with cited sources.
    """
    formatted_time = datetime.utcnow().strftime("%A, %B %d, %Y %H:%M:%S UTC")

    search_query = generate_search_query(query)
    if verbose:
        print(f"Searching \"{search_query}\"...")
    links, sources = search(search_query)

    result = openai.ChatCompletion.create(
        model=COMPLETION_MODEL,
        messages=[
            {"role": "system", "content": "Generate a comprehensive and informative answer for a given question solely based on the provided web Search Results (URL and Summary). You must only use information from the provided search results. Use an unbiased and journalistic tone. Use this current date and time: " + formatted_time + ". Combine search results together into a coherent answer. Do not repeat text. Cite search results using [${number}] notation, and don't link the citations. Only cite the most relevant results that answer the question accurately. If different results refer to different entities with the same name, write separate answers for each entity."},
            {"role": "user", "content": ujson.dumps(sources)},
            {"role": "user", "content": query}
        ]
    )["choices"][0]["message"]["content"]

    for i, link in enumerate(links, start=1):
        result = result.replace(f"[{i}]", f"<sup>[[{i}]]({link})</sup>")
        
    return result