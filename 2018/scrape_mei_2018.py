import requests
import json
import csv
from collections import OrderedDict
from bs4 import BeautifulSoup
from us_states import states

base_url = 'https://www.hrc.org'
fieldnames = OrderedDict()
fieldnames['State'] = 1 
fieldnames['City'] = 1 
fieldnames['Score'] = 1 
fieldnames['Link'] = 1 

multirow = [
    'Employment',
    'Housing',
    'Public Accomodations',
    'Non-Discrimination in City Employment',
    'City Contractor Non-Discrimination Ordinance',
    'Youth Bullying Prevention Policy for City Services',
]

levels = ['State', 'County', 'City', 'Available']

def get_cities_in_state(state):
    slug = state.lower().replace(' ', '-')
    url = f'{base_url}/mei/search/{slug}'
    r = requests.get(url)
    text = r.text
    soup = BeautifulSoup(text, 'lxml')
    for script in soup('script'):
        if script.get('data-mei-list') == '':
            return list(json.loads(script.text).values())
    return []

def fix_typos(s):
    s = s.strip()
    s = s.replace('Accomodations', 'Accommodations')
    s = s.replace('Oshkosk', 'Oshkosh')
    return s

def get_city_data(city, state):
    url = base_url + city['link']
    data = {}
    data['State'] = state
    data['City'] = fix_typos(city['name'])
    data['Link'] = url
    data['Score'] = city['score']
    r = requests.get(url)
    text = r.text
    soup = BeautifulSoup(text, 'lxml')
    row_names = [fix_typos(td.text) for td in soup('td', class_='mei-table__row-name')]
    values = [td.text for td in soup('td', class_='mei-table__td')]
    rows = [f'{row} -- {level}' for row in row_names for level in ['State', 'County', 'City', 'Available']]
    assert len(rows) == len(values)
    for row, val in zip(rows, values):
        if val == 'Not Applicable' or row.endswith('Available'):
            continue
        if any(row.startswith(m) for m in multirow):
            row1 = row + ' -- Sexual Orientation'
            fieldnames[row1] = 1 
            data[row1] = int(val[0])
            row = row + ' -- Gender Identity'
            data[row] = int(val[1])
        else:
            data[row] = int(val)
        fieldnames[row] = 1 
    return data

def get_mei_data():
    rows = []
    for state in states:
        for city in get_cities_in_state(state):
            data = get_city_data(city, state)
            rows.append(data)
            print(city['name'], state, sep=', ')
    return rows

def write_mei_data():
    rows = get_mei_data()
    with open('mei_2018.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_mei_data()
