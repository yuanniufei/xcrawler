#!/usr/bin/env python3
# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : douban_movie.py
# Date   : 2017-01-09 21:20
# Version: 0.0.1
# Description: description of this file.

import json
import random
import string

from bs4 import BeautifulSoup
from lxml.html import fromstring, tostring

from xcrawler import CrawlerProcess
from xcrawler.spider import BaseSpider, Request

__version__ = '0.0.1'
__author__ = 'Chris'


class DoubanMovieSpider(BaseSpider):
    name = 'douban_movie_spider'
    start_urls = ['https://movie.douban.com/tag/爱情',
                  'https://movie.douban.com/tag/喜剧',
                  'https://movie.douban.com/tag/动画',
                  'https://movie.douban.com/tag/动作',
                  'https://movie.douban.com/tag/史诗',
                  'https://movie.douban.com/tag/犯罪']

    default_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36',
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._movie_file = None

    def spider_started(self):
        self._movie_file = open('douban_movies.jl', 'w')

    def spider_stopped(self):
        if self._movie_file:
            self._movie_file.close()

    def parse(self, response):
        html_root = fromstring(response.content, base_url=response.base_url)

        for movie_url in html_root.xpath('//tr[@class="item"]/td/div/a/@href'):
            yield Request(movie_url, cookies=response.cookies,
                          headers=self.default_headers, callback=self.parse_movie_details)

        # Next page
        try:
            next_page_url = html_root.xpath('//span[@class="next"]/a/@href')[0]
        except:
            pass
        else:
            yield Request(next_page_url, cookies=response.cookies,
                          headers=self.default_headers,
                          callback=self.parse)

    def parse_movie_details(self, response):
        html_root = fromstring(response.content, base_url=response.base_url)

        movie_info = dict()
        movie_info['片名'] = self._xpath_first(html_root, '//div[@id="content"]/h1/span[1]/text()').strip()

        # 这里，我们将电影信息转换成纯文本提取
        # 这里写 XPATH 可能不太方便
        soup = BeautifulSoup(tostring(self._xpath_first(html_root, '//div[@id="info"]')))
        for line in soup.get_text().splitlines():
            try:
                left, *right = line.split(':')
                key = left.strip()
                value = ''.join(x.strip() for x in right)

                if key and value:
                    movie_info[key] = value
            except:
                pass

        yield movie_info

    def process_item(self, item):
        # pprint.pprint(item)
        print(json.dumps(item, ensure_ascii=False, sort_keys=True), file=self._movie_file)

    def process_request(self, request):
        request.cookies.update({'bid': self._random_bid()})

    @staticmethod
    def _xpath_first(node, exp, default=''):
        try:
            return node.xpath(exp)[0]
        except:
            return default

    @staticmethod
    def _random_bid():
        return ''.join(random.sample(string.ascii_letters + string.digits, 11))


def main():
    settings = {
        'download_delay': 0.1,
        'download_timeout': 12,
        'retry_on_timeout': True,
        'concurrent_requests': 16,
        'queue_size': 4096
    }
    crawler = CrawlerProcess(settings, 'DEBUG')
    crawler.crawl(DoubanMovieSpider)
    crawler.start()


if __name__ == '__main__':
    main()
