"""Get team locations from html pages downloaded on USAU.org."""
from lxml import html
import csv

pages = ("TeamRankings_Mens.html",
         "TeamRankings_Mixed.html",
         "TeamRankings_Womens.html")
pages = ["ultiscores\\" + x for x in pages]
divs = ("Mens", "Mixed", "Womens")
for ii, div in enumerate(divs):
    tree = html.parse(pages[ii])
    rows = tree.xpath("//tbody/tr")
    teams = []
    towns = []
    states = []
    for row in rows[1:]:
        if len(row) > 5:
            team_text = row[1].text_content()
            team_text = team_text.strip('\n !')
            teams.append(team_text)

            town_text = row[5].text_content()
            town_text = town_text.strip('\n ')
            towns.append(town_text)

            state_text = row[6].text_content()
            town_text = town_text.strip('\n ')
            states.append(state_text)

    data = list(zip(teams, towns, states))
    with open("ultiscores\\hometowns_" + div + ".csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
