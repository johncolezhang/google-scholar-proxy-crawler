#!/usr/bin/env python2

import logging

import pandas as pd

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s - %(message)s')
import os
import requests
from bs4 import BeautifulSoup
import time

from ParseOut import ParseOutYear, ParseOutTitle, ParseOutContent, ParseOutTag, ParseOutURL


class Spider:

    def __init__(self, url,
                 score_level=0,
                 parser='lxml',
                 googleScholarURL="http://scholar.google.com.hk"):
        self.url = url
        self.p_key = []
        self.n_key = []
        self.score_level = score_level
        self.key_score = {}
        self.weighting = {}
        self.parser = parser
        self.__googleScholarURL = googleScholarURL
        self.headers = {
            'Host': 'scholar.google.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
            'Alt-Used': 'scholar.google.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
        }

    def get_result(self, content):
        soup = BeautifulSoup(content, self.parser)
        return self.__crawlPage(soup)


    def crawl(self, keyword, start=0, page=0, proxy=None):
        logger = logging.getLogger('crawl')
        
        page_urls = []
        for i in range(page):
            t_start = 10 * i + start
            page_urls.append(self.url.format(t_start, keyword))

        results = []
        for index, page_url in enumerate(page_urls):
            if proxy:
                res = requests.get(page_url, headers=self.headers, proxies={"http": "http://{}".format(proxy)})
            else:
                res = requests.get(page_url, headers=self.headers)
            soup = BeautifulSoup(res.text, self.parser)
            print("You are now in page ", (index + 1), " !!!")

            ### Test if the crawler is blocked by the Google robot check
            page_links = soup.select('div[id="gs_nml"] a')
            if not page_links:
                logger.info('1.Google robot check might ban you from crawling!!')
                logger.info('2.You might not crawl the page of google scholar')

            ### Try to crawl the page no matter it might be banned by Google robot check
            results += self.__crawlPage(soup, index + 1)
            time.sleep(4)

        return results

    def __crawlPage(self, soup, page_index=0):
        logger = logging.getLogger('__crawlBlock')

        counter = 0
        results = []
        blocks = soup.select('div[class="gs_r gs_or gs_scl"]')
        for block in blocks:
            counter += 1
            result = {}
            try:
                b_title = block.select('h3 a')[0].text #Title
                result['title'] = b_title
            except:
                ### If there is no title in this block, ignore this block
                logger.debug("No Title in Page %s Block %s", page_index, counter)
                result['title'] = ""

            try:
                b_content = block.select('div[class="gs_rs"]')[0].text #Content
                result['content'] = b_content
            except:
                logger.debug("No Content in Page %s Block %s", page_index, counter)
                result['content'] = ""

            try:
                b_url = block.select('h3 a')[0]['href']
                b_url = ParseOutURL(b_url)
                result['url'] = b_url
            except:
                ### If there is no URL in this block, ignore this block
                logger.debug("No URL in Page %s Block %s", page_index, counter)
                result['url'] = ""

            try:
                b_year = block.select('div[class="gs_a"]')[0].text
                result['sub_title'] = b_year
                b_year = ParseOutYear(b_year)
                result['year'] = b_year
            except:
                logger.debug("No Year in Page %s Block %s", page_index, counter)
                result['year'] = ""
                result['sub_title'] = ""

            results.append(result)

        return results


def parse():
    path = "page"
    file_list = list(filter(lambda x: ".html" in x, [os.path.join(path, x) for x in os.listdir(path)]))
    spi = Spider(url="")
    result_list = []
    for fl in file_list:
        with open(fl, "r", encoding="utf-8") as f:
            result_list.extend(spi.get_result(f.read()))

    pd.DataFrame(result_list).to_csv("output/plant_genome_sequencing.csv", index=False)

if __name__ == "__main__":
    parse()