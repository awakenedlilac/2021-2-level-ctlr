"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import shutil
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
from core_utils.article import Article

class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Total number of articles to parse is too big
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    Total number of articles to parse in not integer
    """

class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        self.urls.append('https://gazeta.ru' + article_bs.find('a')['href'])


    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url)
            response.encoding = 'utf-8'
            page_bs = BeautifulSoup(response.text, features='html.parser')
            content_bs = page_bs.find_all('div', class_='b_ear-title')
            for article_bs in content_bs:
                if len(self.urls) < self.max_articles:
                    self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls

class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', class_='b_article-text')
        self.article.text = text_bs.text


    def _fill_article_with_meta_information(self, article_bs):
        title_bs = article_bs.find('div', class_='headline')
        self.article.title = title_bs

        author_bs = article_bs.find('div', class_='author')
        self.article.author = author_bs

    def parse(self):
        response = requests.get(self.article_url)
        response.encoding = 'utf-8'
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']
    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError
    prepare_environment(ASSETS_PATH)
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE

    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls, max_articles)
    crawler.find_articles()

    for i, url in enumerate(crawler.urls):
        parser = HTMLParser(url, i+1)
        article = parser.parse()
        article.save_raw()

