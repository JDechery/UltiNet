# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UltiscoresItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    home = scrapy.Field()
    away = scrapy.Field()
    homescore = scrapy.Field()
    awayscore = scrapy.Field()
    date = scrapy.Field()
    tourney = scrapy.Field()
    div = scrapy.Field()
    
