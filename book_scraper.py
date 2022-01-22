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

    def get_book_details(self):
        """get book details from books urls and save it to output.csv
        """

        # create output.csv file
        output_cols = ['title', 'author(s)', 'year', 'edition',
                                'publisher', 'language', 'pages', 'category(s)', 'ISBN_13', 'rating(5)']
        BooksScraper.create_csv(*output_cols)

        # get books urls
        books_urls = self.get_books_urls()

        # get book details
        for url in tqdm(books_urls, desc='Scraping', unit='book'):
            try:
                book_html = requests.get(url).text
                book_parsed_html = BeautifulSoup(book_html, 'lxml')
                main_div = book_parsed_html.find(
                    'div', {'class': 'col-sm-9'})
            except Exception as e:
                continue

            else:
                # book title
                try:
                    title = main_div.h1.text.strip()
                except Exception as e:
                    title = None

                # book author
                try:
                    authors = main_div.find_all('a', {'itemprop': 'author'})
                    if len(authors) == 1:
                        author = authors[0].text.strip()
                    else:
                        author_list = []
                        for i in range(len(authors)):
                            author_list.append(authors[i].text.strip())
                        author = ', '.join(author_list)
                except Exception as e:
                    author = None

                # book rating
                try:
                    rating = float(main_div.find(
                        'span', {'class': 'book-rating-interest-score'}).text)
                except Exception as e:
                    try:
                        rating = float(main_div.find(
                            'span', {'class': 'book-rating-interest-score none'}).text)
                    except Exception as e:
                        rating = None

                # book category
                try:
                    category = main_div.find(
                        'div', {'class': 'bookProperty property_categories'}).find(
                        'div', {'class': 'property_value'}).a.text.strip()
                except Exception as e:
                    category = None

                # book year
                try:
                    year = main_div.find(
                        'div', {'class': 'bookProperty property_year'}).find(
                        'div', {'class': 'property_value'}).text.strip()
                except Exception as e:
                    year = None

                # book edition
                try:
                    edition = main_div.find(
                        'div', {'class': 'bookProperty property_edition'}).find(
                        'div', {'class': 'property_value'}).text.strip()
                except Exception as e:
                    edition = None

                # book publisher
                try:
                    publisher = main_div.find(
                        'div', {'class': 'bookProperty property_publisher'}).find(
                        'div', {'class': 'property_value'}).text.strip()
                except Exception as e:
                    publisher = None

                # book language
                try:
                    language = main_div.find(
                        'div', {'class': 'bookProperty property_language'}).find(
                        'div', {'class': 'property_value'}).text.strip()
                except Exception as e:
                    language = None

                # book pages
                try:
                    pages = main_div.find(
                        'div', {'class': 'bookProperty property_pages'}).find(
                        'div', {'class': 'property_value'}).span.text.strip()
                except Exception as e:
                    pages = None

                # book ISBN_13
                try:
                    ISBN_13 = main_div.find(
                        'div', {'class': 'bookProperty property_isbn 13'}).find(
                        'div', {'class': 'property_value'}).text.strip()
                except Exception as e:
                    ISBN_13 = None

                # update output.csv file
                scraping_results = {'title': title, 'author(s)': author, 'year': year, 'edition': edition,
                                    'publisher': publisher, 'language': language, 'pages': pages, 'category(s)': category, 'ISBN_13': ISBN_13, 'rating(5)': rating}
                BooksScraper.update_csv(**scraping_results)
                # sleep for 1 sec to avoid server overloaded
                time.sleep(1)


if __name__ == '__main__':
    scraper = BooksScraper(args.search_keyword)
    scraper.get_book_details()
