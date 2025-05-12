import json
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://revista.spmi.pt/index.php/rpmi/issue/archive'
OUTPUT_FILE = 'first_X_articles.json'
MAX_ARTICLES = 11  #Quantos artigos extrair

results = []

def fetch_html(url):
    print(f"[GET] {url}")
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def extract_issues_from_archive():
    page_num = 1
    articles_extracted = 0

    while articles_extracted < MAX_ARTICLES:
        page_url = f"{BASE_URL}/{page_num}" if page_num > 1 else BASE_URL
        print(f"\n=== Processing Archive Page {page_num} ===")
        articles_extracted = extract_issues_from_page(page_url, articles_extracted)
        page_num += 1

def extract_issues_from_page(archive_url, articles_extracted):
    soup = fetch_html(archive_url)
    issue_list = soup.find('ul', class_="issues_archive")
    
    for issue_item in issue_list.find_all('li'):
        if articles_extracted >= MAX_ARTICLES:
            break
        issue_link = issue_item.a['href']
        print(f"\n--- Found Issue: {issue_item.a.text.strip()} ---")
        articles_extracted = extract_issue_data(issue_link, articles_extracted)
        if articles_extracted >= MAX_ARTICLES:
            break
    
    return articles_extracted

def extract_issue_data(issue_url, articles_extracted):
    soup = fetch_html(issue_url)
    issue_title = soup.find('h1').text.strip()
    issue_date = soup.find('span', class_="value").text.strip()
    print(f"Processing Issue: {issue_title} ({issue_date})")

    section_container = soup.find('div', class_="sections")
    article_blocks = section_container.find_all('div', class_="obj_article_summary")

    for article in article_blocks:
        if articles_extracted >= MAX_ARTICLES:
            break
        article_title = article.h3.a.text.strip()
        print(f"  -> Extracting article: {article_title}")
        data = extract_article_data(article.h3.a['href'], issue_date)
        results.append(data)
        articles_extracted += 1
        if articles_extracted >= MAX_ARTICLES:
            break

    return articles_extracted

def extract_article_data(article_url, publish_date):
    soup = fetch_html(article_url)
    section = soup.find('article', class_="obj_article_details")
    entry = section.find('div', class_="main_entry")

    titulo = section.h1.text.strip()

    doi_tag = entry.find('section', class_='item doi')
    doi = doi_tag.a['href'] if doi_tag else None

    abstract_section = entry.find('section', class_="item abstract")
    abstract = " ".join(p.text.strip() for p in abstract_section.find_all('p')) if abstract_section else None

    return {
        'titulo': titulo,
        'abstract': abstract,
        'doi': doi,
        'publish_data': publish_date,
    }

if __name__ == '__main__':
    extract_issues_from_archive()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nDone! {len(results)} articles saved to '{OUTPUT_FILE}'")
