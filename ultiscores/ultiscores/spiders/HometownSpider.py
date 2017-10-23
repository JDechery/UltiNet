from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from ultiscores.items import UltiscoresItem


class MySpider(BaseSpider):
    name = "tester"
    allowed_domains = ["usaultimate.org"]
    start_urls = ["http://play.usaultimate.org/events/TCT-Pro-Elite-Challenge-2016-Colorado-Cup/schedule/Men/Club-Men/"]

    def parse(self, response):
        hxs = Selector(response)
        poolgames = hxs.xpath("//tr[@data-game]")
        bracketgames = hxs.xpath("//div[contains(@id, 'game')]")
        items = []

    for game in poolgames:
        item = UltiscoresItem()
        item["home"] = game.xpath("td/span[@data-type='game-team-home']/a/text()").extract()
        item["away"] = game.xpath("td/span[@data-type='game-team-away']/a/text()").extract()
        item["homescore"] = game.xpath("td/span/span[@data-type='game-score-home']/text()").extract()
        item["awayscore"] = game.xpath("td/span/span[@data-type='game-score-away']/text()").extract()
        gamedate = game.xpath("td/span[@data-type='game-date']/text()").extract()
        gamedate = gamedate[0].split(' ')
        item["date"] = gamedate[1]
        items.append(item)
    for game in bracketgames:
        item = UltiscoresItem()
        item["home"] = game.xpath("div[contains(@class, 'top')]/span[@class='isName']/span/a/text()").extract()
        item["away"] = game.xpath("div[contains(@class, 'btm')]/span[@class='isName']/span/a/text()").extract()
        item["homescore"] = game.xpath("div[contains(@class, 'top')]/span[@class='isScore']/span/text()").extract()
        item["awayscore"] = game.xpath("div[contains(@class, 'btm')]/span[@class='isScore']/span/text()").extract()
        gamedate = game.xpath("span[@class='date']/text()").extract()
        #gamedate = gamedate[0].split(' ')
        item["date"] = gamedate[0].split(' ')[0]
        items.append(item)

    return items
