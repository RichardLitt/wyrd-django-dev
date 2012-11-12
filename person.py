#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module implements the Person class.

"""


class Person():
    """
    Person models, most importantly, the user. This is our future playground
    for machine learning and psychological experiments with learning user
    habits. To that purpose, history of the user's activity shall be stored
    with these objects. Which aspects of the history are stored shall be
    configurable by the user. User's personal configuration settings shall be
    done in a separate file but stored in this class at the same time.

    In future use, this class will also include people other than the local
    user, such as his/her boss, spouse etc. Those people might or might not be
    using Wyrd In. If they don't, they will be known just by their identifier
    and their relation to the current user, so that they are recognised as the
    same person in future interactions with the local user. Even if they use
    Wyrd In too, they should have many fields hidden to the local user. Sharing
    of personal data shall be configurable by each user and have rather
    restrictive default setting.

    """
    raise NotImplementedError("Person needs to be implemented yet.")
    pass
