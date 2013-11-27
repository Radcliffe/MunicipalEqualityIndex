#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Dave
#
# Created:     26/11/2013
# Copyright:   (c) Dave 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib2
import time
import collections
import lxml.html
from geopy import geocoders
g = geocoders.GoogleV3()

def most_common(lst):
    return max(set(lst), key=lst.count)

def get_filename(cityno):
    return "../HTML/profile%03d.html" % cityno

def get_url(cityno):
    return "http://www.hrc.org/apps/mei/profile.php?id=" + str(cityno)

def download_html():
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    for cityno in range(2, 294):
        response = opener.open(get_url(cityno))
        html = response.read()
        f = open(get_filename(cityno), "wt")
        f.write(html)
        f.close()
        time.sleep(0.5)

def get_lat_lon(cityname):
    try:
        standard_name, (lat, lon) = g.geocode(cityname, exactly_one=False)[0]
        print "%s is located at Latitude %s, Longitude %s" % (cityname, lat, lon)
        time.sleep(0.5)
        return lat, lon
    except ValueError:
        print "****** %s not located!" % cityname
        return '', ''

def write_csv():
    # download_html()
    output = []
    for cityno in range(2, 294):
        f = open(get_filename(cityno), 'rt')
        html = ''.join(f.readlines())
        f.close()
        doc = lxml.html.fromstring(html)
        cityname = [elt.text_content() for elt in doc.iter('h2')][1]
        city, state = cityname.split(',')
        city = city.strip()
        state = state.strip()
        lat, lon = get_lat_lon(cityname)
        table = doc.iter('table').next()
        actualSO = [elt.text_content() for elt in table.find_class('actualSO')]
        actualGI = [elt.text_content() for elt in table.find_class('actualGI')]
        row = [city, state, str(lat), str(lon)] + actualSO + actualGI
        state_total = sum(int(row[i-1]) for i in [5,8,11,14,15,16,31,42,45,48,53])
        county_total = sum(int(row[i-1]) for i in [6,9,12,17,32,43,46,49,54])
        city_total = doc.find_class('final')[-1].text_content()
        row.extend([str(state_total), str(county_total), city_total])
        output.append(','.join(row)+'\n')
    f = open('MEI.csv', 'wt')
    f.writelines(output)
    f.close()

def aggregate_by_state():
    f = open('MEI.csv', 'rt')
    output = []
    lines = f.readlines()
    f.close()

    rows = [line.split(',') for line in lines]
    states = sorted(list(set([row[1] for row in rows])))
    for state in states:
        state_idx = [k for k in xrange(len(rows)) if rows[k][1] == state]
        outrow = [state]
        for field in [5,8,11,14,15,16,31,42,45,48,53]:
            mode = most_common([rows[k][field-1] for k in state_idx])
            outrow.append(mode)
        outrow.append(str(sum(map(int,outrow[1:]))))
        output.append(','.join(outrow)+'\n')

    f = open('MEI-states.csv', 'wt')
    f.writelines(output)
    f.close()

def validate_state_data():

    f = open('MEI.csv', 'rt')
    lines = f.readlines()
    f.close()
    city_rows = [line.strip().split(',') for line in lines]

    f = open('MEI-states.csv', 'rt')
    lines = f.readlines()
    f.close()
    state_rows = [line.strip().split(',') for line in lines]

    g = open("../MEI_Codebook.csv", 'rt')
    lines = g.readlines()
    g.close()
    codes = [line.split(',') for line in lines]

    fields = [5,8,11,14,15,16,31,42,45,48,53,56]

    output = ["City,State,Category,Type,Issue,Expected,Actual\n"]
    for row in city_rows:
        state_idx = None
        for i in xrange(len(state_rows)):
            if row[1] == state_rows[i][0]:
                state_idx = i
                break
        else:
            print "Error - State not found!"
            quit()
        for i in xrange(len(fields)):
            expected = state_rows[state_idx][i+1]
            actual = row[fields[i]-1]

            if expected != actual:
                category = codes[fields[i]][1]
                Type = codes[fields[i]][3]
                issue = codes[fields[i]][4]
                output.append(','.join([row[0], row[1], category, Type, issue, expected, actual])+'\n')
                row[fields[i]-1] = expected


    f = open('MEI-errors.csv', 'wt')
    f.writelines(output)
    f.close()

    f = open('MEI-revised.csv', 'wt')
    f.writelines([','.join(row)+'\n' for row in city_rows])
    f.close()

if __name__ == '__main__':
    # download_html()
    # write_csv()
    # aggregate_by_state()
    validate_state_data()
