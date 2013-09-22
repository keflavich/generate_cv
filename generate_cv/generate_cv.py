# -*- coding: utf-8 -*-

import dateutil.parser
import requests
import astropy.io.votable as votable
import os
import codecs

def get_dev_key():
    """ A convenience function for accessing a system-wide ADS Developer's Key """

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


htmlfmtstr = (u'                '
              u'<li><a class="norm" href="http://adsabs.harvard.edu/abs/{adsbibid}">{creator}</a>'
              u' {month}, <b>{year}</b> {journal}\n'
              u'                <br>&nbsp;&nbsp;&nbsp;{titlestring}')


def wrangle(data, authorname='Ginsburg'):
    """ Create new fields from the input data to insert into the format string """

    data['month'] = data['pubdate'][5:7]
    
    # Generally, the last identifier is the published version, 
    # while the first is an arXiv identifier
    # (data['identifier'] is a list)
    data['adsbibid'] = data['identifier'][-1]

    # data['title'] & ['pub'] are also lists
    data['titlestring'] = data['title'][0]
    data['journal'] = data['pub'][0]

    # This trick bolds my name in the list of authors
    data['authors'] = ['<b>{}</b>'.format(x) if authorname in x else x for x in data['author']]

    # Separate names by semicolons
    data['creator'] = u"; ".join(data['authors'])

    return data



def write_html(author='ginsburg, a', outfile='generated.html', fmt=htmlfmtstr):
    J = request_author_data(author)
    datalist = J['results']['docs']

    with codecs.open('generated.html','w',encoding='utf8') as outf:
        for data in datalist:
            print >>outf,fmt.format(**wrangle(data))
