#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import json
from WebCrawler.items import WebcrawlerItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    start_urls = ['http://g1.globo.com/politica/']
    pages_depth = 3 # Is overwritten at Spider start (main)
    pages_visited_number = 0
    train_file = ''

    def parse(self, response):
        self.pages_visited_number += 1
        posts = response.css('.post-item')
        for post in posts:
            # follow links to news pages
            href = post.css('a.feed-post-link::attr(href)').extract_first()

            item = WebcrawlerItem()
            item['url'] = href
            item['title'] = post.css('p.feed-post-body-title::text').extract_first()
            item['abstract'] = post.css('p.feed-post-body-resumo::text').extract_first() if len(post.css('p.feed-post-body-resumo::text')) > 0 else ''

            if item['title'] in self.get_viseted_pages_title():
                return

            request = scrapy.Request(href, callback=self.parse_author)
            request.meta['item'] = item
            yield request

        #  Next page
        next_page = response.css('div.load-more a::attr(href)').extract_first()
        if next_page is not None and self.pages_visited_number < self.pages_depth:
            next_page = 'http://g1.globo.com/' + next_page
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_author(self, response):
        item = response.meta['item']
        print('processing ' + item['url'])
        raw_date = (response.css('time::text').extract_first())
        item['date'] = re.search( r'(((\d{2})\/(\d{2})\/(\d{4}))|((\d{2})-(\d{2})-(\d{4})))', raw_date, re.M|re.I).group().replace('-', '/') + " " + \
                       re.search( r'((\d{2}):(\d{2})|(\d{2})h(\d{2}))', raw_date, re.M|re.I).group().replace('h', ':')
        text = ""
        for p in response.css('div.mc-article-body').css('p.content-text__container ::text').extract():
            text += p

        if text != "":
            item['text'] = text
            yield item

    def get_viseted_pages_title(self):
        content = open(self.train_file, 'r')
        for line in content:
            line = json.loads(line)['title']
            yield line