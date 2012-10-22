#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module implements the Scheduler class.

"""


class Scheduler():
    """
    Scheduler is the active role in the Wyrd In system. It tries to order known
    tasks towards some criterion, be it the throughput, latency, fairness (cf.
    process scheduling in computers), best fit for available amount time,
    meeting deadlines, exploiting the opportunity, user's mood (perhaps
    specified by the user, or maybe guessed), the horoscope, or something else.
    These different kinds of scheduling should be implemented in subclasses of
    Scheduler, while the user has to retain the ability to switch the
    scheduling algorithm at any time for minimal cost. For that, task schedules
    devised by any scheduler shall be cached. Whenever they need to be
    recomputed, this should be done effectively. Ideally, each change in the
    set of tasks should cause only a local change in the schedule. Moreover,
    many transitions (such as completing the current task) can be guessed, and
    their effect on the schedule can (and should) be precomputed.
    """
    raise NotImplementedError("Scheduler needs to be implemented yet.")
    pass


class Schedule():
    """
    This is the result of Scheduler's work. The format and interface have to be
    determined yet.
    """
    raise NotImplementedError("Schedule needs to be implemented yet.")
    pass
