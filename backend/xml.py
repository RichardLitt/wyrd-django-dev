#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is mostly PEP8-compliant. See
# http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""
from lxml import etree
from datetime import datetime, timedelta
import pytz


# TODO: Inherit from IBackend (to be implemented).
class XmlBackend(object):
    parser = etree.XMLParser(remove_blank_text=True)

    @classmethod
    def _timedelta_repr(cls, td):
        # TODO: Be more human-friendly.
        return '{d} d, {s} s'.format(d=td.days, s=td.seconds)

    @classmethod
    def _timedelta_fromrepr(cls, td_repr):
        parts = td_repr.split()
        return timedelta(days=int(parts[0]), seconds=int(parts[2]))

    @classmethod
    def _create_task_e(cls, session, task):
        """Creates an XML element for an object of the type Task."""
        task_e = etree.Element("task",
                               project=task.project,
                               done=str(int(task.done)))
        if 'time' in task.__dict__:
            task_e.set('time', cls._timedelta_repr(task.time))
        if 'deadline' in task.__dict__:
            task_e.set('deadline', datetime.strftime(
                task.deadline, session.config['CFG_TIME_FORMAT_REPR']))
            if task.deadline.tzinfo:
                task_e.set('deadline_tz', task.deadline.tzname())
        task_e.text = task.name
        return task_e

    @classmethod
    def write_tasks(cls, session, tasks, outfile, standalone=True):
        """Writes out a list of tasks in the XML format to the open file
        `outfile'.

        Keyword arguments:
            - session: the global object for the user session
            - tasks: an iterable of objects of the type Task
            - outfile: a file open for writing, to which the tasks should be
                       written
            - standalone: whether a complete XML content should be written to
                          the file, including the XML header

        """
        tasks_e = etree.Element('tasks')
        for task in tasks:
            tasks_e.append(cls._create_task_e(session, task))
        outfile.write(etree.tostring(tasks_e,
                                     encoding='UTF-8',
                                     pretty_print=True,
                                     xml_declaration=standalone))

    @classmethod
    def read_tasks(cls, session, infile):
        from task import Task
        tasks = []
        for _, elem in etree.iterparse(infile):
            # Stop reading as soon as the </tasks> tag is encountered.
            if elem.tag == "tasks":
                break
            # Otherwise, parse each <task> element in accordance to the way it
            # was output.
            attrs = elem.attrib
            # XXX When project of a task becomes something more than just
            # a string, the code will probably break on the following line.
            task = Task(name=elem.text, project=attrs['project'])
            if 'done' in attrs:
                task.done = bool(int(attrs['done']))
            if 'time' in attrs:
                task.time = cls._timedelta_fromrepr(attrs['time'])
            if 'deadline' in attrs:
                task.deadline = datetime.strptime(
                    attrs['deadline'],
                    session.config['CFG_TIME_FORMAT_REPR'])
                if 'deadline_tz' in attrs:
                    task.deadline = task.deadline.replace(
                        tzinfo=pytz.timezone(attrs['deadline_tz']))
            tasks.append(task)
        return tasks
