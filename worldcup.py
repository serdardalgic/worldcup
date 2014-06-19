import argparse
import sys
import json
import datetime

import colorama
import humanize
import dateutil.parser
import dateutil.tz

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


FUTURE = "future"
NOW = "now"
PAST = "past"
SCREEN_WIDTH = 68

FIFA_CODE_DICT = {
    "Brazil": "BRA",
    "Croatia": "CRO",
    "Mexico": "MEX",
    "Cameroon": "CMR",
    "Spain": "ESP",
    "Netherlands": "NED",
    "Chile": "CHI",
    "Australia": "AUS",
    "Colombia": "COL",
    "Greece": "GRE",
    "Ivory Coast": "CIV",
    "Japan": "JPN",
    "Uruguay": "URU",
    "Costa-Rica": "CRC",
    "England": "ENG",
    "Italy": "ITA",
    "Switzerland": "SUI",
    "Ecuador": "ECU",
    "France": "FRA",
    "Honduras": "HON",
    "Argentina": "ARG",
    "Bosnia-Herzegovina": "BIH",
    "Iran": "IRN",
    "Nigeria": "NGA",
    "Germany": "GER",
    "Portugal": "POR",
    "Ghana": "GHA",
    "USA": "USA",
    "Belgium": "BEL",
    "Algeria": "ALG",
    "Russia": "RUS",
    "South Korea": "KOR",
}
GROUP_DICT = dict(zip(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], range(1, 9)))


def country_code(cname):
    try:
        return cname if cname in FIFA_CODE_DICT.values() else FIFA_CODE_DICT[
            cname]
    except KeyError:
        print ("You should either give the name or FIFA Country Code "
               "of one of the following countries:")
        for cnt, code in FIFA_CODE_DICT.items():
            print """ {:<20} <--> {} """.format(cnt, code)
        sys.exit(-2)


def progress_bar(percentage, separator="o", character="-"):
    """
    Creates a progress bar by given percentage value
    """
    filled = colorama.Fore.GREEN + colorama.Style.BRIGHT
    empty = colorama.Fore.WHITE + colorama.Style.BRIGHT

    if percentage == 100:
        return filled + character * SCREEN_WIDTH

    if percentage == 0:
        return empty + character * SCREEN_WIDTH

    completed = int((SCREEN_WIDTH / 100.0) * percentage)

    return (filled + (character * (completed - 1)) +
            separator +
            empty + (character * (SCREEN_WIDTH - completed)))


def prettify(match):
    """
    Prettifies given match object
    """
    diff = (datetime.datetime.now(tz=dateutil.tz.tzlocal()) -
            dateutil.parser.parse(match['datetime']))

    seconds = diff.total_seconds()

    if seconds > 0:
        if seconds > 60 * 90:
            status = PAST
        else:
            status = NOW
    else:
        status = FUTURE

    if status in [PAST, NOW]:
        color = colorama.Style.BRIGHT + colorama.Fore.GREEN
    else:
        color = colorama.Style.NORMAL + colorama.Fore.WHITE

    home = match['home_team']
    away = match['away_team']

    if status == NOW:
        minute = int(seconds / 60)
        match_status = "Being played now: %s minutes gone" % minute
    elif status == PAST:
        if match['winner'] == 'Draw':
            result = 'Draw'
        else:
            result = "%s won" % (match['winner'])
        match_status = "Played %s. %s" % (humanize.naturaltime(diff),
                                                  result)
    else:
        match_status = "Will be played %s" % humanize.naturaltime(diff)

    if status == NOW:
        match_percentage = int(seconds / 60 / 90 * 100)
    elif status == FUTURE:
        match_percentage = 0
    else:
        match_percentage = 100

    return u"""
    {} {:<30} {} - {} {:>30}
    {}
    \u26BD  {}
    """.format(
        color,
        home['country'],
        home['goals'],
        away['goals'],
        away['country'],
        progress_bar(match_percentage),
        colorama.Fore.WHITE + match_status
    )

def group_list(country):
    """
    Lists a group member
    """
    return """
    {:<22} | {:5} |{:7} |{:10} |{:14} | {}
    {}
    ---------------------------------------------------------------------------
    """.format(
        country['country'],
        country['wins'],
        country['losses'],
        country['goals_for'],
        country['goals_against'],
        country['knocked_out'],
        "-" * SCREEN_WIDTH
    )


def is_valid(match):
    """
    Validates the given match object
    """
    return (
        isinstance(match, dict) and
        isinstance(match.get('home_team'), dict) or
        isinstance(match.get('away_team'), dict) or
        isinstance(match.get('group_id'), int)
    )


def fetch(endpoint):
    """
    Fetches match results by given endpoint
    """
    url = "http://worldcup.sfg.io/%(endpoint)s?by_date=ASC" % {
        "endpoint": endpoint
    }

    data = urlopen(url).read().decode('utf-8')
    matches = json.loads(data)

    for match in matches:
        if is_valid(match):
            yield match


def parse_args():
    parser = argparse.ArgumentParser(
        description="World Cup results for hackers. Uses Soccer For Good API.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--country", help="Name or the FIFA code of "
                       "the country.", default="", dest="country")
    group.add_argument("-g", "--group", help="Name of the group to see "
                       "the standings.",
                       choices=GROUP_DICT.keys(),
                       default="")
    group.add_argument("-p", "--period",
                       help="Time period that you want to know the match "
                       "results.",
                       choices=("today", "tomorrow", "current"),
                       default="")
    return parser.parse_args()


def main():
    colorama.init()
    args = parse_args()

    if args.group:
        endpoint = 'group_results'
        group_id = GROUP_DICT[args.group]
        print """    GROUP {:<20}""".format(args.group)
        print " " * 3, "-" * 75
        print """    {:<22} | {:5} | {:<5} | {:<5} | {:<5} | {:<5}
        """.format("Country", "wins", "losses", "Goals For",
                   "Goals Against", "Out?")

        #print ("      Country       |"
               #"  wins:  |  losses  | Goals For | Goals Against | Out?")

        for match in fetch(endpoint):
            if (match.get('group_id') == group_id):
                print group_list(match)
    else:
        endpoint = 'matches/'
        if args.country:
            endpoint += 'country?fifa_code=%(country)s' % {
                "country": country_code(args.country)
            }
        elif args.period:
            endpoint += args.period

        for match in fetch(endpoint):
            print(prettify(match).encode('utf-8'))

if __name__ == "__main__":
    main()
