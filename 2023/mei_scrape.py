import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import os.path


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

SEARCH_URL = 'https://www.hrc.org/resources/municipalities/search'

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


def read_us_states():
    # Read in the list of US states. Returns a dictionary with keys 'State' and 'Abbreviation'
    with open('us_states.csv', 'r') as f:
        reader = csv.DictReader(f)
        us_states = list(reader)
    return us_states


def get_first_page_for_state(state_name):
    # Get the HTML page for a given state. Return as a BeautifulSoup object
    time.sleep(0.5)
    response = requests.get(SEARCH_URL, params={'q': state_name}, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')


def get_additional_page_for_state(next_page_link):
    time.sleep(0.5)
    response = requests.get(next_page_link, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')


def get_next_page_links(state_page):
    # Get the links to the next pages of the search results
    next_page_links = state_page.find_all('a', href=True)
    next_page_links = [link['href'] for link in next_page_links if link['href'].startswith(SEARCH_URL)]
    return next_page_links[1: -1]  # Skip the first and last links


def get_municipality_links_on_page(state_page, state_abbr):
    # Get the links to the municipalities on the current page
    munis = state_page.find_all('a', href=True)
    munis = [link['href']
             for link in munis
             if link['href'].startswith('https://www.hrc.org/resources/municipalities/')
             and '/search' not in link['href']
             and link['href'].endswith('-' + state_abbr.lower())]
    return munis


def get_municipality_links_for_state(state_name, state_abbr):
    # Get the links to the municipalities for a given state
    state_page = get_first_page_for_state(state_name)
    munis = get_municipality_links_on_page(state_page, state_abbr)
    next_page_links = get_next_page_links(state_page)
    for next_page_link in next_page_links:
        next_page = get_additional_page_for_state(next_page_link)
        munis += get_municipality_links_on_page(next_page, state_abbr)
    return munis


def get_all_municipality_links():
    states = read_us_states()
    municipalities = []
    city_id = 0
    for state in states:
        state_name = state['State']
        state_abbr = state['Abbreviation']
        print(f'Getting municipalities for {state_name}...')
        for link in get_municipality_links_for_state(state_name, state_abbr):
            city_id += 1
            city_name = link.split('/')[-1].rsplit('-' + state_abbr.lower(), 1)[0].replace('-', ' ').title()
            municipalities.append({
                'City Id': city_id,
                'State': state_name,
                'State Abbreviation': state_abbr,
                'Municipality': city_name,
                'Link': link
            })
    with open('cities.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['City Id', 'State', 'State Abbreviation', 'Municipality', 'Link'])
        writer.writeheader()
        writer.writerows(municipalities)


def load_cities():
    with open('cities.csv', 'r') as f:
        return list(csv.DictReader(f))


def load_template():
    with open('template.csv', 'r') as f:
        return list(csv.DictReader(f))


def get_scores():
    cities = load_cities()
    template = load_template()
    data = []
    row_id = 0
    for city in cities:
        city_id = int(city['City Id'])
        city_name = city['Municipality']
        state = city['State Abbreviation']
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
    return data


def get_score_totals_by_municipality(muni_data):
    print('Generating point totals for each municipality.')
    scores = [int(row['Score']) for row in muni_data]
    rows = []
    for i in range(0, len(scores), 49):
        first = muni_data[i]
        city_id = int(first['City Id'])
        assert city_id == i // 49 + 1
        nondisc = min(30, sum(scores[i: i+18]))
        muni_empl = min(28, sum(scores[i+24: i+30]))
        muni_svcs = min(12, sum(scores[i+31: i+36]))
        law_enforce = min(22, sum(scores[i+43: i+45]))
        leadership = min(8, sum(scores[i+45: i+47]))
        total_points = min(100, sum(scores[i: i+49]))
        flex_points = total_points - nondisc - muni_empl - muni_svcs - law_enforce - leadership
        rows.append({
            'City Id': city_id,
            'City': first['City'],
            'State': first['State'],
            'Non-Discrimination Laws': nondisc,
            'Municipality as Employer': muni_empl,
            'Municipal Services': muni_svcs,
            'Law Enforcement': law_enforce,
            'Leadership on LGBTQ+ Equality': leadership,
            'Flex Points': flex_points,
            'Total Score': total_points,
        })
    with open('mei-totals-by-municipality-2023.csv', 'w') as f:
        fieldnames = ('City Id', 'City', 'State', 'Non-Discrimination Laws',
                      'Municipality as Employer', 'Municipal Services', 'Law Enforcement', 
                      'Leadership on LGBTQ+ Equality', 'Flex Points', 'Total Score')
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test():
    url = 'https://www.hrc.org/resources/municipalities/newport-news-va'
    page = retrieve_page(url)
    scores = list(get_scores_on_page(page))
    template = load_template()
    for score, row in zip(scores, template):
        print(score, row['Category'], row['Criterion'], row['Level of government'], row['Orientation/Identity'])


def main():
    if os.path.isfile('cities.csv'):
        print('File cities.csv already exists, skipping.')
    else:
        get_all_municipality_links()
    if os.path.isfile('mei-data-2023.csv'):
        data = None
        print('File mei-data-2023.csv already exists, skipping.')
    else:
        data = get_scores()
    if os.path.isfile('mei-totals-by-municipality-2023.csv'):
        print('File mei-totals-by-municipality-2023.csv exists, skipping.')
    else:
        if data is None:
            with open('mei-data-2023.csv', 'r') as f:
                data = list(csv.DictReader(f))
        get_score_totals_by_municipality(data)


if __name__ == '__main__':
    main()
