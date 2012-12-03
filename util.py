#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

This module collects rather universal utility functions.

"""


def group_by(objects, attrs, single_attr=False):
    """Groups `objects' by the values of their attributes `attrs'.

    Returns a dictionary mapping from a tuple of attribute values to a list of
    objects with those attribute values.

    keyword arguments:
        - single_attr: specifies that there is just one attribute to use as the
                       key, and that the keys should be directly values of the
                       attribute, rather than one-tuples

    """
    # Specifying one string shall be interpreted as the single attribute name,
    # rather than a sequence of one-letter attribute names.
    if isinstance(attrs, str):
        attrs = (attrs, )
    if single_attr and len(attrs) != 1:
        raise ValueError("single_attr specified, but multiple attrs used " + \
                         "for indexing.")
    if single_attr:
        attr = attrs[0]

    groups = dict()
    for obj in objects:
        if single_attr:
            key = obj.__dict__[attr]
        else:
            key = tuple(obj.__dict__[attr] for attr in attrs)
        groups.setdefault(key, []).append(obj)
    return groups


def format_timedelta(timedelta):
     whole_repr = str(timedelta) + '.'
     return whole_repr[:whole_repr.find('.')]
