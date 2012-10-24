#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module implements classes related to time definitions.

"""
# TODO: Find whether (part of) this functionality is already provided by
# Python libraries.
# ...Yes, it is. See the `datetime', `calendar' and `time' standard libraries.


# class TimeSpan():
#     pass


# class Instant():
#     pass


class WorkSlot(TimeSpan):
    """ This shall be a time span (or `timedelta' in Python terminology) with
    the annotation saying how it was spent. It shall link to the relevant task
    (or, perhaps, a list of concurrently performed tasks). The annotations
    should include facts like start time, end time, concentration devoted to
    the task (may be in relation to the number of simultaneously performed
    tasks), comments, state of the task before and after this work slot.
    """
    raise NotImplementedError("WorkSlot needs to be implemented yet.")
    pass
