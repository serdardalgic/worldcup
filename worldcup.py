import sys
import json
from urllib.request import urlopen
import datetime

import pytz
import colorama
import humanize
import dateutil.parser


FUTURE = "future"
NOW = "now"
PAST = "past"
SCREEN_WIDTH = 68


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
    Prints a match object
    """
    diff = (datetime.datetime.now(pytz.timezone("UTC")) -
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
        match_status = "Being played: %s. minute" % minute
    elif status == PAST:
        match_status = "Played %s. Winner: %s" % (humanize.naturaltime(diff),
                                                  match['winner'])
    else:
        match_status = "Will be played after %s" % humanize.naturaltime(diff)

    if status == NOW:
        match_percentage = int(seconds / 60 / 90 * 100)
    elif status == FUTURE:
        match_percentage = 0
    else:
        match_percentage = 100

    return """
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


def is_valid(match):
    """
    Validates the given match object
    """
    return (
        isinstance(match, dict) and
        isinstance(match.get('home_team'), dict) or
        isinstance(match.get('away_team'), dict)
    )


def fetch(endpoint):
    """
    Fetches match results by given endpoint
    """
    url = "http://worldcup.sfg.io/matches/%(endpoint)s" % {
        "endpoint": endpoint
    }

    data = urlopen(url).read().decode('utf-8')
    matches = json.loads(data)

    for match in matches:
        if is_valid(match):
            yield match


def main():
    colorama.init()
    endpoint = ''.join(sys.argv[1:])
    for match in fetch(endpoint):
        print(prettify(match))


if __name__ == "__main__":
    main()
