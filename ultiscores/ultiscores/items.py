# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UltiscoresItem(scrapy.Item):
    """Scrapy item to collect score reports."""

    home = scrapy.Field()
    away = scrapy.Field()
    homescore = scrapy.Field()
    awayscore = scrapy.Field()
    date = scrapy.Field()
    tourney = scrapy.Field()
    div = scrapy.Field()


class Team(scrapy.Item):
    """Scrapy item to collect team locations."""

    teamname = scrapy.Field()
    hometown = scrapy.Field()
