#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urllib
import unicodecsv
import argparse
import math
import datetime
from lxml import html

YELLOW_PAGES_URL = "https://www.yellowpages.com"
USA_STATES = ['AA', 'AE', 'AK', 'AL', 'AP', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC ', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']

def go_fetch(niches):

    print ("ScrapeHound is in the USA")
    go_fetch_yellow_pages(niches)


def go_fetch_yellow_pages(niches):

    for niche in niches:

        print ("ScrapeHound is going fetch {0} in the Yellow Pages".format(niche))

        for state in USA_STATES:

            print ("ScrapeHound is currently in {0}".format(state))

            page_number = 1            
            current_scraped_results = go_fetch_yellow_pages_page(niche, state, page_number)

            if (current_scraped_results):
                
                all_scraped_results = []
                all_scraped_results.extend(current_scraped_results)

                listing_result_pages = int(current_scraped_results[0]['listing_result_pages'])

                while page_number < listing_result_pages:

                    page_number = page_number + 1
                    current_scraped_results = go_fetch_yellow_pages_page(niche, state, page_number)
                    all_scraped_results.extend(current_scraped_results)

                fieldnames = ['rank', 'business_name', 'telephone', 'business_page', 'category', 'email', 'website', 'rating',
                            'street', 'locality', 'region', 'zipcode', 'listing_url', 'listing_result_pages']

                write_csv_file('%s-%s-yellowpages-scraped-data.csv' % (niche, state), fieldnames, all_scraped_results)       


def write_csv_file(filename, fieldnames, rows):
    with open(filename, 'wb') as csvfile:
        writer = unicodecsv.DictWriter(csvfile, fieldnames=fieldnames, quoting=unicodecsv.QUOTE_ALL)
        writer.writeheader()
        for data in rows:
            writer.writerow(data)        


def go_fetch_yellow_pages_page(niche, state, page):

    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.yellowpages.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }

    params = urllib.parse.urlencode({'search_terms': niche, 'geo_location_terms': state, 'page': page})           

    listings_page_url = "{0}/search?{1}".format(YELLOW_PAGES_URL, params)

    print("ScrapeHound is currently fetching from this {0} listing page: {1}".format(state, listings_page_url))

    listings_response = requests.get(listings_page_url, headers=headers)

    for retry in range(10):

        if listings_response.status_code == 200:

            listings_parser = html.fromstring(listings_response.text)
                    
            listings_parser.make_links_absolute(YELLOW_PAGES_URL)

            pages = 1

            if page == 1:

                try:

                    XPATH_PAGINATION_INFO_TEXT = "//div[@class='pagination'][1]//text()"
                    raw_pagination_info_text = listings_parser.xpath(XPATH_PAGINATION_INFO_TEXT)

                    if raw_pagination_info_text:
                        raw_pagination_text = ''.join(raw_pagination_info_text).strip().replace("We found", "").replace("results12345Next", "").replace("resultsPrevious12345Next", "")

                        # There are 30 records per page
                        pages = math.ceil(int(raw_pagination_text) / 30)

                except:

                    print("ScrapeHound had an retrieving the number of pages for {0}".format(state))


            XPATH_LISTINGS = "//div[@class='search-results organic']//div[@class='v-card']"
            listings = listings_parser.xpath(XPATH_LISTINGS)

            scraped_results = []

            for listings_html in listings:

                XPATH_BUSINESS_NAME = ".//a[@class='business-name']//text()"
                XPATH_BUSSINESS_PAGE = ".//a[@class='business-name']//@href"
                XPATH_TELEPHONE = ".//div[@class='phones phone primary']//text()"
                XPATH_ADDRESS = ".//div[@class='info']//div//p[@itemprop='address']"
                XPATH_STREET = ".//div[@class='street-address']//text()"
                XPATH_LOCALITY = ".//div[@class='locality']//text()"
                XPATH_REGION = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='addressRegion']//text()"
                XPATH_ZIP_CODE = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='postalCode']//text()"
                XPATH_RANK = ".//div[@class='info']//h2[@class='n']/text()"
                XPATH_CATEGORIES = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='categories']//text()"
                XPATH_WEBSITE = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='links']//a[contains(@class,'website')]/@href"
                XPATH_RATING = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"

                raw_business_name = listings_html.xpath(XPATH_BUSINESS_NAME)
                raw_business_telephone = listings_html.xpath(XPATH_TELEPHONE)
                raw_business_page = listings_html.xpath(XPATH_BUSSINESS_PAGE)
                raw_categories = listings_html.xpath(XPATH_CATEGORIES)
                raw_website = listings_html.xpath(XPATH_WEBSITE)
                raw_rating = listings_html.xpath(XPATH_RATING)
                raw_street = listings_html.xpath(XPATH_STREET)
                raw_locality = listings_html.xpath(XPATH_LOCALITY)
                raw_region = listings_html.xpath(XPATH_REGION)
                raw_zip_code = listings_html.xpath(XPATH_ZIP_CODE)
                raw_rank = listings_html.xpath(XPATH_RANK)

                business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
                business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                rank = ''.join(raw_rank).replace('.\xa0', '') if raw_rank else None
                category = ','.join(raw_categories).strip() if raw_categories else None
                email = ''
                website = ''.join(raw_website).strip() if raw_website else None
                rating = ''.join(raw_rating).replace("(", "").replace(")", "").strip() if raw_rating else None
                street = ''.join(raw_street).strip() if raw_street else None
                locality = ''.join(raw_locality).replace(',\xa0', '').strip() if raw_locality else None
                locality_parts = ''
                region = ''
                zipcode = ''
                if locality:
                    locality, locality_parts = locality.split(',')
                    _, region, zipcode = locality_parts.split(' ')

                if business_page:
                    try:

                        business_info_response = requests.get(business_page, headers)

                        if business_info_response.status_code == 200:

                            business_info_parser = html.fromstring(business_info_response.text)

                            XPATH_BUSINESS_INFO = "//div[@class='business-card clearfix paid-listing'][1]//a[@class='email-business'][1]//text()"
                            
                            business_info = listings_parser.xpath(XPATH_BUSINESS_INFO)  

                            business_info_html = html.fromstring(requests.get(business_page, headers=headers).text)

                            for email_html in business_info_html.cssselect('a.email-business'):
                                email = email_html.attrib['href'].replace("mailto:","")

                    except:

                        print("ScrapeHound had an error getting the email for {0}".format(business_name))

                business_details = {    
                    'business_name': business_name,
                    'telephone': telephone,
                    'business_page': business_page,
                    'rank': rank,
                    'category': category,
                    'email': email,
                    'website': website,
                    'rating': rating,
                    'street': street,
                    'locality': locality,
                    'region': region,
                    'zipcode': zipcode,
                    'listing_url': listings_response.url,
                    'listing_result_pages': pages
                }
                scraped_results.append(business_details)

            return scraped_results        
            
        elif listings_response.status_code == 404:
            print("ScrapeHound couldn't find any results for {0} page {1}".format(state, page))
            break
        else:
            print("ScrapeHound ran into an unexpected issue for {0} page {1}".format(state, page))
            return []
     

def main(niches_raw_list):

    print ("Unleashing ScrapeHound at {0}".format(datetime.datetime.now()))

    niches_formatted_list = []
    
    for raw_niche in niches_raw_list:
        niches_formatted_list.append(raw_niche.strip())

    go_fetch(niches_formatted_list)

    print ("ScrapeHound was done at {0}".format(datetime.datetime.now()))


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('niches', help='Search Niches', nargs='+') 

    args = argparser.parse_args()
    print("args.niches value: {0}".format(args.niches))

    niches_raw_list = args.niches

    main(niches_raw_list)