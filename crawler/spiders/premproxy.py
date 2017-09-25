# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from crawler.helper import get_list_item_safely
from crawler.items import PremProxyItemLoader, Proxy


class PremProxySpider(CrawlSpider):
    name = 'premproxy'
    allowed_domains = ['premproxy.com']
    start_urls = [
        'https://premproxy.com/list/',
        'https://premproxy.com/socks-list/'
    ]

    rules = (Rule(
        LinkExtractor(allow=('\d+.htm$',), deny=('ip-.*.htm', 'type-.*.htm', 'time-.*.htm')),
        callback='parse_item'
    ),)

    def parse_item(self, response):
        is_socks = response.url.find('socks') > -1
        proxies = []
        rows = response.css('.container > table > tbody > tr')
        for row in rows:
            loader = PremProxyItemLoader(item=Proxy(), selector=row)
            ip_port = get_list_item_safely(row.css('td:nth-child(1)::text').extract(), 0).split(':')
            # ip addresss and port
            loader.add_value('ip_address', [get_list_item_safely(ip_port, 0, 'localhost')])
            loader.add_value('port', [get_list_item_safely(ip_port, 1, 80)])
            # for socks, here should use css selector to extract else use default HTTP
            _type = ['HTTP']
            if is_socks:
                _type = row.css('td:nth-child(2)::text').extract()
            loader.add_value('type', _type)
            # for socks, use default elite else use css selector to extract
            _anonymity = ['elite']
            if not is_socks:
                _anonymity = row.css('td:nth-child(2)::text').extract()
            loader.add_value('anonymity', _anonymity)
            loader.add_css('last_check_at', 'td:nth-child(3)::text')
            country = get_list_item_safely(row.css('td:nth-child(4)::text').extract(), 0)
            city = get_list_item_safely(row.css('td:nth-child(5)::text').extract(), 0)
            loader.add_value('location', [country + ', ' + city])
            proxies.append(loader.load_item())
        return proxies