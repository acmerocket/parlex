import dateparser
import datetime
import re

# borrowed from https://github.com/jlev/parler-etl/blob/master/transform-post-html-to-jsonl.py
def parse_datetime(timestr, origin_time):
    """
    Attempts to parse an approximate datetime from the provided string.
    :param timestamp: a freeform string describing a timestamp
    :param time_offset: a deltatime used to offset dates for timestamps such as ´1 day ago´ or ´2 hours ago´
    :return:
    """
    if timestr is None:
        return None

    dt_parsed = dateparser.parse(timestr, languages=['en'])

    try:
        if re.search('[a-zA-Z]', timestr):
            dt_approx = dt_parsed - origin_time
        else:
            dt_approx = dateparser.parse(timestr, languages=['en'])
        return dt_approx
    except Exception as e:
        print(f"Failed to parse datetime with timestamp: {timestr}, offset: {origin_time}: {e}")
        return None
    except KeyboardInterrupt:
        raise