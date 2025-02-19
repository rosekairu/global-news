import json
import requests
import ssl
from .models import NewsArticle, Sources


api_key = None  # Initialize API key

def configure_request(app):
    """ Configure API key from app settings. """
    global api_key
    api_key = app.config['NEWS_API_KEY']


def get_news(country, category):
    """ Fetch top news headlines based on country and category. """
    get_news_url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={api_key}"

    response = requests.get(get_news_url)

    if response.status_code == 200:
        get_news_response = response.json()
        if get_news_response.get('articles'):
            return process_news_results(get_news_response['articles'])
    
    return None


def process_news_results(news_list):
    """ Process news articles into NewsArticle objects. """
    news_results = []

    for news_item in news_list:
        source = news_item.get('source', {})
        source_name = source.get('name', 'Unknown')
        
        author = news_item.get('author', source_name)
        if not author or author.strip() == "" or len(author) > 40 or author.startswith("http"):
            author = source_name

        title = news_item.get('title')
        url = news_item.get('url')
        image_url = news_item.get('urlToImage')
        published_at = news_item.get('publishedAt')
        published = date_pipe(published_at)
        description = news_item.get('description')
        content = news_item.get('content')

        news_object = NewsArticle(source_name, author, title, url, image_url, published, description, content)
        news_results.append(news_object)

    return news_results


def news_from_source(source_id):
    """ Fetch news from a specific source. """
    get_url = f"https://newsapi.org/v2/everything?sources={source_id}&pageSize=30&apiKey={api_key}"

    response = requests.get(get_url)

    if response.status_code == 200:
        get_response = response.json()
        if get_response.get('articles'):
            return process_news_results(get_response['articles'])

    return []

def get_sources():
    """ Fetch available news sources. """
    get_sources_url = f"https://newsapi.org/v2/sources?country=us&category=general&language=en&apiKey={api_key}"

    response = requests.get(get_sources_url)

    if response.status_code == 200:
        get_sources_response = response.json()
        if get_sources_response.get('sources'):
            return process_sources_results(get_sources_response['sources'])

    return None

def process_sources_results(sources_list):
    """ Process news sources into Sources objects. """
    sources_results = []

    for source in sources_list:
        source_id = source.get('id')
        source_name = source.get('name')

        source_obj = Sources(source_id, source_name)
        sources_results.append(source_obj)

    return sources_results


def search_topic(query):
    """ Search for news articles based on a topic query. """
    search_topic_url = f"https://newsapi.org/v2/everything?q={query}&sortBy=relevancy,publishedAt&pageSize=30&apiKey={api_key}"

    response = requests.get(search_topic_url)

    if response.status_code == 200:
        search_topic_response = response.json()
        if search_topic_response.get('articles'):
            return process_news_results(search_topic_response['articles'])

    return None


def search_from_source(query, source):
    """ Search for news articles from a specific source. """
    search_topic_url = f"https://newsapi.org/v2/everything?q={query}&sortBy=relevancy,publishedAt&pageSize=30&sources={source}&apiKey={api_key}"

    response = requests.get(search_topic_url)

    if response.status_code == 200:
        search_topic_response = response.json()
        if search_topic_response.get('articles'):
            return process_news_results(search_topic_response['articles'])

    return None

def date_pipe(date):
    """ Convert date format from ISO to 'DD/MM/YYYY - HH:MM hrs' """
    if date:
        return f"{date[8:10]}/{date[5:7]}/{date[0:4]} - {date[11:16]} hrs"
    return "Unknown Date"
