import requests
from bs4 import BeautifulSoup
import re
import csv
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

session = requests.Session()
session.headers.update(headers)


def retrieve_page(url, params=None):
    response = session.get(url, params=params)
    return BeautifulSoup(response.text, 'html.parser')


def get_scores_on_page(page):
    cells = page.select('td.w-140:not(.border-1)')
    for cell in cells:
        text_contents = cell.text
        if text_contents.strip() == '':
            print('Missing value on page, assuming 0.')
            yield 0
        else:
            scores = re.findall(r'\d+', text_contents)
            for score in scores:
                yield int(score)


def load_cities():
    with open('cities.csv', 'r') as f:
        return list(csv.DictReader(f))


def load_template():
    with open('template.csv', 'r') as f:
        return list(csv.DictReader(f))


def main():
    cities = load_cities()
    template = load_template()
    data = []
    row_id = 0
    for city in cities:
        city_id = int(city['Row Id'])
        city_name = city['City']
        state = city['Abbreviation']
        link = city['Link']
        time.sleep(.5)
        print(f'Retrieving data for {city_name}, {state}')
        page = retrieve_page(link)
        scores = list(get_scores_on_page(page))
        template_copy = template[:]
        if len(scores) != len(template_copy):
            print(f'Found {len(scores)} scores, expected {len(template_copy)}.')
        for row, score in zip(template_copy, scores):
            new_row = dict(row)
            row_id += 1
            new_row['Row Id'] = row_id
            new_row['City Id'] = city_id
            new_row['City'] = city_name
            new_row['State'] = state
            new_row['URL'] = link
            new_row['Score'] = score
            new_row['Score Id'] = int(new_row['Score Id'])
            # print(new_row)
            data.append(new_row)
    with open('mei-data-2023.csv', 'w') as f:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def test():
    url = 'https://www.hrc.org/resources/municipalities/newport-news-va'
    page = retrieve_page(url)
    scores = list(get_scores_on_page(page))
    template = load_template()
    for score, row in zip(scores, template):
        print(score, row['Category'], row['Criterion'], row['Level of government'], row['Orientation/Identity'])


if __name__ == '__main__':
    main()
    # test()
