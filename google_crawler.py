#!/usr/bin/env python

import pandas as pd
from Spider import Spider

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def main(keyword, start=0, page=10, proxy=None):
    ### The start page's URL
    template_url = 'https://scholar.google.com/scholar?start={}&q={}&hl=zh-cn&as_sdt=0,5&as_ylo=2001'

    ### Google Scholar Crawler, Class Spider
    myCrawler = Spider(template_url)

    results = myCrawler.crawl(keyword=keyword.replace(" ", "+"), start=start, page=page, proxy=proxy)

    pd.DataFrame(results).to_csv("output/{}_{}.csv".format(keyword.replace(" ", "_"), start), index=False)

if __name__ == '__main__':
    keyword = "plant genome sequencing"
    
    proxy = None
    while not proxy:
    	proxy = get_proxy().get("proxy")

    for i in range(4):
        main(keyword, start=i * 100, proxy=proxy) # every time download 100 paper's info
