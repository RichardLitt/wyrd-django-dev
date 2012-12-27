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
                               id=str(task.id),
                               done=str(int(task.done)))
        if 'project' in task.__dict__ and task.project is not None:
            task_e.set('project', task.project)
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
        if standalone:
            top_e = wyrdin_e = etree.Element('wyrdinData')
            tasks_e = etree.SubElement(wyrdin_e, 'tasks')
        else:
            top_e = tasks_e = etree.Element('tasks')
        for task in tasks:
            tasks_e.append(cls._create_task_e(session, task))
        outfile.write(etree.tostring(top_e,
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
            elif elem.tag == "task":
                attrs = elem.attrib
                # XXX When project of a task becomes something more than just
                # a string, the code will probably break on the following line.
                if 'project' in attrs:
                    project = attrs['project']
                else:
                    project = ''
                task = Task(name=elem.text,
                            project=project,
                            id=int(attrs['id']))
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

    @classmethod
    def _create_slot_e(cls, session, slot):
        """Creates an XML element for an object of the type WorkSlot."""
        slot_e = etree.Element('workslot',
                               id=str(slot.id),
                               task=str(slot.task.id))
        if slot.start is not None:
            slot_e.set('start', datetime.strftime(
                slot.start, session.config['CFG_TIME_FORMAT_REPR']))
        if slot.end is not None:
            slot_e.set('end', datetime.strftime(
                slot.end, session.config['CFG_TIME_FORMAT_REPR']))
        return slot_e

    @classmethod
    def write_workslots(cls, session, slots, outfile, standalone=True):
        if standalone:
            top_e = wyrdin_e = etree.Element('wyrdinData')
            slots_e = etree.SubElement(wyrdin_e, 'workslots')
        else:
            top_e = slots_e = etree.Element('workslots')
        for slot in slots:
            slots_e.append(cls._create_slot_e(session, slot))
        outfile.write(etree.tostring(top_e,
                                     encoding='UTF-8',
                                     pretty_print=True,
                                     xml_declaration=standalone))

    @classmethod
    def read_workslots(cls, session, infile):
        from worktime import WorkSlot
        slots = []
        for _, elem in etree.iterparse(infile):
            # Stop reading as soon as the </workslots> tag is encountered.
            if elem.tag == "workslots":
                break
            # Otherwise, parse each <workslot> element in accordance to the way
            # it was output.
            elif elem.tag == "workslot":
                attrs = elem.attrib
                id_ = int(attrs['id'])
                task_id = int(attrs['task'])
                task = session.get_task(task_id)
                start = (datetime.strptime(
                            attrs['start'],
                            session.config['CFG_TIME_FORMAT_REPR'])
                         if 'start' in attrs else None)
                end = (datetime.strptime(
                            attrs['end'],
                            session.config['CFG_TIME_FORMAT_REPR'])
                       if 'end' in attrs else None)
                slot = WorkSlot(task=task, start=start, end=end, id=id_)
                slots.append(slot)
        return slots

    # XXX This name is not the best possible. `all' still does not include
    # projects, just tasks and work slots.
    @classmethod
    def write_all(cls, session, tasks, slots, outfile):
        """Writes out a list of tasks and work slots in the XML format to the
        open file `outfile'.

        Keyword arguments:
            - session: the global object for the user session
            - tasks: an iterable of objects of the type Task
            - slots: an iterable of objects of the type WorkSlot
            - outfile: a file open for writing, to which the tasks should be
                       written

        """
        wyrdin_e = etree.Element('wyrdinData')
        tasks_e = etree.SubElement(wyrdin_e, 'tasks')
        slots_e = etree.SubElement(wyrdin_e, 'workslots')
        for task in tasks:
            tasks_e.append(cls._create_task_e(session, task))
        for slot in slots:
            slots_e.append(cls._create_slot_e(session, slot))
        outfile.write(etree.tostring(wyrdin_e,
                                     encoding='UTF-8',
                                     pretty_print=True,
                                     xml_declaration=True))
