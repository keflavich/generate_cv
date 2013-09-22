# -*- coding: utf-8 -*-

import dateutil.parser
import requests
import astropy.io.votable as votable
import os
import codecs

def get_dev_key():

    ads_dev_key_filename = os.path.abspath(os.path.expanduser('~/.ads/dev_key'))

    if os.path.exists(ads_dev_key_filename):
        with open(ads_dev_key_filename, 'r') as fp:
            dev_key = fp.readline().rstrip()

        return dev_key

    if 'ADS_DEV_KEY' in os.environ:
        return os.environ['ADS_DEV_KEY']

    raise IOError("no ADS API key found in ~/.ads/dev_key")


def request_author_data(author='ginsburg, a'):
    response = requests.post('http://adslabs.org/adsabs/api/search/',
                         params={'q':'author:{}'.format(author),
                                 'dev_key':get_dev_key(),
                                 'rows':200,
                                 'filter':'database:astronomy'})

    J = response.json()

    return J


htmlfmtstr = u'''                <li><a class="norm" href="http://adsabs.harvard.edu/abs/{identifier}">{creator}</a> {month}, <b>{year}</b> {journal}
                <br>&nbsp;&nbsp;&nbsp;{title}'''

def wrangle(data):
    #date = dateutil.parser.parse(data['pubdate']) 
    data['month'] = data['pubdate'][5:7] # date.month
    #data['year'] = date.year
    data['identifier'] = data['identifier'][0] if isinstance(data['identifier'],list) else data['identifier']
    data['title'] = data['title'][0] if isinstance(data['title'],list) else data['title']
    data['journal'] = data['pub'][0] if isinstance(data['pub'],list) else data['pub']
    data['author'] = ['<b>{}</b>'.format(x) if 'Ginsburg' in x and not '<b>' in x else x for x in data['author']]
    data['author'] = [x.replace("\\x","&#") for x in data['author']]
    data['creator'] = u"; ".join(data['author'])
    return data


def write_html(author='ginsburg, a', outfile='generated.html', fmt=htmlfmtstr):
    J = request_author_data(author)
    datalist = J['results']['docs']

    with codecs.open('generated.html','w',encoding='utf8') as outf:
        for data in datalist:
            print >>outf,fmt.format(**wrangle(data))
