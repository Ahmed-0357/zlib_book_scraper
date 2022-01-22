import argparse
import csv
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# receive user search keyword from command line
parser = argparse.ArgumentParser(
    description='use search keyword to collect books details from ZLibary website')
parser.add_argument('search_keyword', type=str,
                    help='can be title, author, ISBN, publisher')
args = parser.parse_args()


class BooksScraper:
    """scrape books details from ZLibary website (https://my1lib.org/)
    """

    def __init__(self, search_keyword):
        """create instance variables 
        Args:
            search_keyword (str): search keyword can be title, author, ISBN, publisher
        """
        self.search_keyword = search_keyword.replace(' ', '%20')
        self.page = 1
        self.search_link = f'https://my1lib.org/s/{self.search_keyword}?page={self.page}'

    @staticmethod
    def create_csv(*args):
        """create output.csv file to save books details 
        """
        header = (args)
        with open('output.csv', 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    @staticmethod
    def update_csv(**kwargs):
        """update output.csv file 
        """
        data = list(kwargs.values())
        with open('output.csv', 'a', newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    def get_books_urls(self):
        """get books urls from all pages
        Returns:
            [list]: list contains books urls
        """
        books_urls = []
        while True:
            # get books urls in the currant page
            page_html = requests.get(self.search_link).text
            page_parsed_html = BeautifulSoup(page_html, 'lxml')

            books = page_parsed_html.find_all(
                'table', {'class': 'resItemTable'})
            for book in books:
                try:
                    book_url = 'https://my1lib.org'+book.h3.a['href']
                except Exception as e:
                    continue

                books_urls.append(book_url)

            # move to next page
            next_page_num = page_parsed_html.find(
                'div', {'class': 'paginator'}).a['href'].split('?')[-1].split('=')[-1]
            try:
                # update search link
                self.page = int(next_page_num)
                self.search_link = f'https://my1lib.org/s/{self.search_keyword}?page={self.page}'
            except Exception as e:
                break

        return books_urls


if __name__ == '__main__':
    scraper = BooksScraper(args.search_keyword)
    urls = scraper.get_books_urls()
    print(urls)
