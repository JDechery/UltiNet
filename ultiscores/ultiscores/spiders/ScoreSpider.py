import scrapy
from scrapy.http import Request
from scrapy.spider import CrawlSpider, Rule
from scrapy.selector import Selector
from ultiscores.items import UltiscoresItem


class MySpider(CrawlSpider):
    name = "scorereport"
    allowed_domains = ["usaultimate.org"]
    start_urls = ["http://play.usaultimate.org/events/tournament/?ViewAll=true&IsLeagueType=false&IsClinic=false&FilterByCategory=AE&SeasonId=6&EventTypeId=16&EventSubTypeId=47"]
    
    #generate requests for each tournament page
    def parse_start_url(self,response):
        #convert xpath text output to list of divisions
        def parse_divisions(divisions):
            cleanDivs = []
            for div in divisions:
                if any(c.isalpha() for c in div):
                    cd = div.strip('\r').strip('\n').strip(' ')
                    cd = cd.split(' ')[-1].lower()
                    cleanDivs.append(cd)
            return cleanDivs
        #append division paths to tournament URL
        def appendTournamentURL(tournamentPageURL, divisions):
            divs = ['/schedule/' + div + '/club-' + div + '/' for div in divisions]
            return [tournamentPageURL+suffix for suffix in divs]
        
        hxs = Selector(response)
        #get list of events
        tourney_list = hxs.xpath("//tbody/tr")
        requests = []
        for tourney in tourney_list:
            #get links
            url = tourney.xpath("td/a/@href").extract()
            url = url[0].encode('utf-8')
            #get divisions
            divisions = tourney.xpath("td/ul/li/text()").extract()
            divisions = parse_divisions(divisions)
            divisions = [x.encode('utf-8') for x in divisions]
            #create response objects
            if divisions is not None:
                full_urls = appendTournamentURL(url,divisions)
                for link in full_urls:
                    self.logger.info('Adding request for %s', link)
                    requests.append(Request(link, callback=self.parse_games))
        return requests
    
    #collect results from tourney pages
    def parse_games(self, response):
        self.logger.info('Processing response from %s', response.url)
        hxs = Selector(response)
        #find division and tournament name
        division = hxs.xpath("//h1[@class='title']/text()").extract()
        division = division[0].split(' ')[2]
        tourney = hxs.xpath("//div[@class='breadcrumbs']/a[2]/text()").extract()
        #pool play and bracket play have different html structure
        poolgames = hxs.xpath("//tr[@data-game]")
        bracketgames = hxs.xpath("//div[contains(@id, 'game')]")
        items = []
        for game in poolgames:
            try:
                item = UltiscoresItem()
                home = game.xpath("td/span[@data-type='game-team-home']/a/text()").extract()
                item["home"] = home[0]
                away = game.xpath("td/span[@data-type='game-team-away']/a/text()").extract()
                item["away"] = away[0]
                homescore = game.xpath("td/span/span[@data-type='game-score-home']/text()").extract()
                item["homescore"] = homescore[0]
                awayscore = game.xpath("td/span/span[@data-type='game-score-away']/text()").extract()
                item["awayscore"] = awayscore[0]
                gamedate = game.xpath("td/span[@data-type='game-date']/text()").extract()
                gamedate = gamedate[0].split(' ')
                item["date"] = gamedate[1]
                item["tourney"] = tourney[0]
                item["div"] = division
                items.append(item)
            except:
                self.logger.error('error processing tournament %s',response.url)
                continue
        for game in bracketgames:
            try:
                item = UltiscoresItem()
                home = game.xpath("div[contains(@class, 'top')]/span[@class='isName']/span/a/text()").extract()
                item["home"] = home[0]
                away = game.xpath("div[contains(@class, 'btm')]/span[@class='isName']/span/a/text()").extract()
                item["away"] = away[0]
                item["homescore"] = str(game.xpath("div[contains(@class, 'top')]/span[@class='isScore']/span/text()").extract()[0])
                item["awayscore"] = str(game.xpath("div[contains(@class, 'btm')]/span[@class='isScore']/span/text()").extract()[0])
                gamedate = game.xpath("span[@class='date']/text()").extract()
                #gamedate = gamedate[0].split(' ')
                item["date"] = gamedate[0].split(' ')[0]
                item["tourney"] = tourney[0]
                item["div"] = division
                items.append(item)
            except:
                self.logger.error('error processing tournament %s',response.url)
                continue        
        return items