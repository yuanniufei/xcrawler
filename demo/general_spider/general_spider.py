#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : general_spider.py
# Date   : 2017-01-14 19:22
# Version: 0.0.1
# Description: description of this file.

import datetime
import json

from lxml.html import fromstring

from xcrawler import CrawlerProcess
from xcrawler.spider import BaseSpider, Request

__version__ = '0.0.1'
__author__ = 'Chris'


class GeneralSpider(BaseSpider):
    name = 'general_spider'
    start_urls = ['http://stackoverflow.com',
                  'https://www.hao123.com/', 'https://123.sogou.com/',
                  'http://www.3456.cc/index.html', 'https://hao.360.cn/']

    default_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crawled_urls = None

    def spider_started(self):
        self.crawled_urls = open('general_spider.jl', 'w')

    def spider_stopped(self):
        if self.crawled_urls:
            self.crawled_urls.close()

    def parse(self, response):
        try:
            html_root = fromstring(response.content, base_url=response.base_url)

            yield {'url': response.url, 'timestamp': str(datetime.datetime.now()),
                   'status': response.status,
                   'title': self._extract_title(html_root),
                   'description': self._extract_description(html_root),
                   'keywords': self._extract_description(html_root)}

            for url in html_root.xpath('//a/@href'):
                if url.startswith('https://') or url.startswith('http://'):
                    yield Request(url, headers=self.default_headers)
        except Exception as err:
            yield {'url': response.url, 'status': response.status,
                   'timestamp': str(datetime.datetime.now()),
                   'error': err}

    def _extract_title(self, node):
        return self._xpath_first(node, '//title/text()').strip()

    def _extract_keywords(self, node):
        return self._xpath_first(node, '//meta[@name="keywords"]/@content').strip()

    def _extract_description(self, node):
        return self._xpath_first(node, '//meta[@name="description"]/@content').strip()

    @staticmethod
    def _xpath_first(node, exp, default=''):
        try:
            return node.xpath(exp)[0]
        except:
            return default

    def process_item(self, item):
        print(json.dumps(item, ensure_ascii=False, sort_keys=True), file=self.crawled_urls)


def main():
    settings = {
        'download_delay': 1,
        'download_timeout': 32,
        'retry_on_timeout': False,
        'concurrent_requests': 512,
        'queue_size': 4096
    }

    crawler = CrawlerProcess(settings, 'DEBUG')
    crawler.crawl(GeneralSpider)
    crawler.start()


if __name__ == '__main__':
    main()
