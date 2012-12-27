#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is mostly PEP8-compliant. See
# http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module implements classes related to time definitions.

"""
import re
from datetime import datetime, timedelta, timezone

from backend.generic import DBObject


# Constants.
zero_delta = timedelta()
_dashes_rx = re.compile('-+')
_float_subrx = r'(?:-\s*)?(?:\d+(?:\.\d+)?|\.\d+)'
_timedelta_rx = re.compile((r'\W*?(?:({flt})\s*d(?:ays?\W+)?\W*?)?'
                        r'(?:({flt})\s*h(?:(?:ou)?rs?\W+)?\W*?)?'
                        r'(?:({flt})\s*m(?:in(?:ute)?s?\W+)?\W*?)?'
                        r'(?:({flt})\s*s(?:ec(?:ond)?s?)?\W*?)?$')\
                            .format(flt=_float_subrx),
                        re.IGNORECASE)


def parse_timedelta(timestr):
    """ Parses a string into a timedelta object.

    """
    rx_match = _timedelta_rx.match(timestr)
    # If the string seems to comply to the format assumed by the regex,
    if rx_match is not None:
        vals = []
        any_matched = False
        # Convert matched groups for numbers into floats one by one.
        for grp_str in rx_match.groups():
            if grp_str:
                any_matched = True
                try:
                    val = float(grp_str)
                except ValueError:
                    raise ValueError('Could not parse float from {grp}.'\
                        .format(grp=grp_str))
            else:
                val = 0
            vals.append(val)
        # If at least one of the groups was present,
        # (In the regex, all time specifications (days, hours etc.) are
        # optional. We have to check here that at least one was supplied.)
        if any_matched:
            return timedelta(days=vals[0], hours=vals[1],
                             minutes=vals[2], seconds=vals[3])
        else:
            rx_match = None
    # If regex did not solve the problem,
    if rx_match is None:
        # Try to interpret the input as a float amount of minutes.
        try:
            return timedelta(minutes=float(timestr))
        except ValueError:
            raise ValueError('Could not parse duration from "{arg}".'\
                            .format(arg=timestr))


def parse_datetime(dtstr):
    """ Parses a string into a datetime object.

    Currently merely interprets the string as a floating point number of days
    from now.

    """
    # TODO Crude NLP.
    # Try to use some keywords.
    keywords = [(re.compile(r"^\s*(?:the\s+)?end\s+of\s+(?:the\s+)?"
                            r"world(?:\s+(?:20|')12)?$"),
                    datetime(year=2012, month=12, day=21,
                             hour=11, minute=11, tzinfo=timezone.utc))]
    lower = dtstr.lower().strip()
    for keyword, dt in keywords:
        if keyword.match(lower):
            return dt

    try:
        return datetime.now() + timedelta(days=float(dtstr))
    except ValueError:
        raise ValueError('Could not parse datetime from "{arg}".'\
                         .format(arg=dtstr))


def daystart(dt=lambda: datetime.now()):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def dayend(dt=lambda: datetime.now()):
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def parse_interval(ivalstr):
    """ Parses a string into an Interval object."""
    now = datetime.now()
    # Try to use some keywords.
    keywords = {'today': (daystart(now), dayend(now))}
    ivalstr = ivalstr.strip()
    if ivalstr.lower() in keywords:
        start, end = keywords[ivalstr.lower()]
        return Interval(start, end)

    # Parse the interval in the form A--B.
    start, end = _dashes_rx.split(ivalstr.strip(), 2)
    start = parse_datetime(start) if start else None
    end = parse_datetime(end) if end else None
    return Interval(start, end)


class Interval(object):
    """ Represents a time interval -- not just its length, but also its
    absolute position (start and end times).

    """

    def __init__(self, start=None, end=None):
        """Initialises the object."""
        if not (start is None or isinstance(start, datetime)) \
           or not (end is None or isinstance(end, datetime)):
            raise TypeError('The `start\' and `end\' arguments have to '
                            'be a `datetime\' instance or None.')
        if start and end and start > end:
            raise ValueError('Start must be earlier than end.')
        self.start = start
        self.end = end

    def __str__(self):
        return '{start!s}--{end!s}'.format(start=self.start,
                                           end=self.end)

    @property
    def length(self):
        if self.start is None or self.end is None:
            return timedelta.max
        return self.end - self.start

    @length.setter
    def length(self, newlength):
        if self.start is None and self.end is None:
            raise ValueError('Cannot set the length for an unbound interval.')
        if self.start is None:
            self.start = self.end - newlength
        else:
            self.end = self.start + newlength

    def intersects(self, other):
        start_after_other_end = self.start is not None \
                                and other.end is not None \
                                and self.start > other.end
        end_before_other_start = self.end is not None \
                                 and other.start is not None \
                                 and self.end < other.start
        return not start_after_other_end and not end_before_other_start

    def includes(self, dt):
        return (self.start is None or self.start <= dt) and \
               (self.end is None or self.end >= dt)

    def iscurrent(self):
        return self.includes(datetime.now())


class WorkSlot(Interval, DBObject):
    """ This shall be a time span (or `timedelta' in Python terminology) with
    the annotation saying how it was spent. It shall link to the relevant task
    (or, perhaps, a list of concurrently performed tasks). The annotations
    should include facts like start time, end time, concentration devoted to
    the task (may be in relation to the number of simultaneously performed
    tasks), comments, state of the task before and after this work slot.

    """

    def __init__(self, task, start, end=None, id=None):
        """Creates a new work slot.

        Keyword arguments:
            - task: an instance of task this work slot refers to
            - start: a datetime instance representing the start of this work
                     slot
            - end: a datetime instance representing the end of this work
                   slot (or None, meaning it has not ended yet)
            - id: the ID (a number) of this work slot as a database object, if
                  a specific one is required

        """
        super().__init__(start, end)
        DBObject.__init__(self, id)
        self.task = task

    def __str__(self):
        return "<WorkSlot: {task}, {invl}>".format(
            task=self.task,
            invl=super().__str__())

    def __repr__(self):
        return self.__str__()
