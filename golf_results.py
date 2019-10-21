""" This Script is fetching Golftournament leaderboards for one season
(chosen by the user and specified by the input of the year in which
this particular season ends)from the espn.com website and appending
them to a fresh csv-file. In its current form the script is only working
for seasons prior to the ongoing season.
"""

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from lxml import html
import csv
import re


def tours():
    """ User has to choose from which tour he wants to get the
    golf results.
    """
    tour = input("Tour? Please type 'pga', "
                 "'lpga', 'champions', 'web' or 'euro'. ")
    if tour == "pga":
        tour_str = ""
    else:
        tour_str = "/tour/" + tour
    return(tour_str)
        

def golfresults():
    """ Start the data collection process. """
    lb_links = schedule(season, tour)
    for lb_link in lb_links:
        leaderboard(lb_link)


def schedule(season, tour):
    """ Fetching the links to the tournament leaderboards of the
    specific tour and season and returning them.
    """
    # Opening site with the tournament schedule of the season in question.
    url = "http://www.espn.com/golf/schedule/_/year/" + str(season) + tour
    html = urlopen(url)
    # Finding the table with the schedule.
    soup = BeautifulSoup(html, 'lxml')
    t_sched = soup.find_all('table', {'class':'tablehead'})
    t_sched_rows = t_sched[0].find_all('tr')
    # Collecting a list with the leaderboard-sites.
    lb_links = []
    for t_sched_row in t_sched_rows[2:]:
        lb_link = t_sched_row.find('a',href=
                    re.compile('(\/golf\/leaderboard.*)')).get('href')
        lb_links.append(lb_link)
    return(lb_links)


def leaderboard(tourney): 
    """ Opening one site with a tournament leaderboard and copying
    this leaderboard to a csv-file.
    """
    espn_id = tourney.split("Id=")[1]
    # Opening a tournament site and bypassing internal server error.
    url = "http://www.espn.com" + str(tourney)
    for i in range(0, 50):
        while True:
            try:
                html = urlopen(url)
            except HTTPError:
                continue
            break
    # Finding title, date and geographic location of the tournament.    
    soup = BeautifulSoup(html, 'lxml')
    tourn_name = soup.find('h1',
                    {'class':'Leaderboard__Event__Title'}).get_text()
    tourn_date = soup.find('span',
                    {'class':'Leaderboard__Event__Date n7'}).get_text()
    course_details = soup.find('div',
                    {'class':'Leaderboard__Courses'}).get_text()
    # Locating the leaderboard-table. 
    tourn_lb = soup.find_all('table', {'class':'Table2__table-scroll'})
    # Naming and Opening csv-file
    if tour == "":
        csv_name = 'golf_results_pga_' + str(season) + '.csv'
    else:
        csv_name = ('golf_results_' + tour.split('tour/')[1] +
                    str(season) + '.csv')
    csv_file = open(csv_name, 'at', newline='\n')
    writer = csv.writer(csv_file, delimiter=';')
    # Controlling the case of having no table on the site.
    try:
        rows = tourn_lb[-1].find_all('tr')
        
        for row in rows[2:]:
            csv_row = []
            for cell in row.find_all(['td']):
                csv_row.append(cell.get_text())
            writer.writerow(([espn_id] + [tourn_name] + [tourn_date] +
                             [course_details] + csv_row))
        csv_file.close()
    except IndexError:
        pass


if __name__ == '__main__':
    tour = tours()
    season = int(input("Season? In its current form the script is only " +
            "working for seasons prior to the ongoing season. (enter '2017' e.g.) "))
    golfresults()