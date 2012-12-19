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

# Constants.
zero_delta = timedelta()
_dashes = re.compile('-+')


def parse_delta(timestr):
    """ Parses a string into a timedelta object.

    Currently merely interprets the string as a floating point number of
    minutes.

    """
    # TODO Crude NLP.
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
    keywords = [(re.compile(r"^end\s+of\s+(the\s+)?world(\s+(20|')12)?$"),
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
    start, end = _dashes.split(ivalstr.strip(), 2)
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
            raise TypeError('The `start\' and `end\' arguments have to be'
                            'a `datetime\' instance or None.')
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


class WorkSlot(Interval):
    """ This shall be a time span (or `timedelta' in Python terminology) with
    the annotation saying how it was spent. It shall link to the relevant task
    (or, perhaps, a list of concurrently performed tasks). The annotations
    should include facts like start time, end time, concentration devoted to
    the task (may be in relation to the number of simultaneously performed
    tasks), comments, state of the task before and after this work slot.

    """

    def __init__(self, task, start=None, end=None):
        super().__init__(start, end)
        self.task = task

    def __str__(self):
        return "<WorkSlot: {task}, {invl}>".format(
            task=self.task,
            invl=super().__str__())

    def __repr__(self):
        return self.__str__()


