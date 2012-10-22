#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module implements the Deadline class.

"""


class Deadline():
    """
    Deadline is an attribute of a task or a goal. It is essentially an instance
    of the datetime.time class, but it can be more complex. We can have soft
    deadlines too. Deadlines can have penalties associated with missing them.
    A deadline always belongs to a certain task or project (goal). The history
    of each deadline (how it was originally specified and later shifted,
    modified or cancelled, potentially also who shifted, modified or cancelled
    it) should be also stored.
    """
    raise NotImplementedError("Deadline needs to be implemented yet.")
    pass
