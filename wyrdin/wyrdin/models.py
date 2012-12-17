from django.db import models
from datetime import datetime, timedelta
from settings import TIME_ZONE


class StateOrEvent(models.Model):
    """This is a common superclass for the State and Event classes. Ofttimes,
    it is underspecified whether State or Event is appropriate for the
    situation. This class comes handy in those situations.

    """
    pass


class State(StateOrEvent):
    """
    This class represents a state of the world in the broadest sense.
    """
    name = models.CharField(max_length=128)
    is_current = models.BooleanField()

    def __str__(self):
        return '<State: {name}>'.format(name=self.name)


class Event(StateOrEvent):
    """
    This class represents a one-time event in the real world in the broadest
    sense.

    """
    name = models.CharField(max_length=128)
    dt_happened = models.DateTimeField(null=True)

    def __str__(self):
        return '<Event: {name}>'.format(name=self.name)


class Project(models.Model):
    """This is a proxy for different levels of goals or themes. In future, we
    should allow for subprojects and superprojects as subgoals and super-goals
    or super-themes.

    """
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return '<Project: {name}>'.format(name=self.name)


class Task(models.Model):
    """
    Task is an (potentially recurrent) event with an actor, generally one that
    is desired by the user. Every task has the actor specified, be it the local
    user or someone else, even a generic `someone'. Tasks generally also have
    deadlines and belong to a plan, even if the plan should consist of a single
    task. There are all other sorts of attributes of tasks, which are to be
    determined as the implementation proceeds.

    Tasks can have a complex recurrency structure. The implementation should
    account for tasks such as ``Take a pill P each Monday and Thursday after
    breakfast.'' or ``Buy and paint eggs two weeks before Easter except for
    leap years.''

    """
    name = models.CharField(max_length=128)
    project = models.ForeignKey(Project)
    prerequisites = models.ManyToManyField(StateOrEvent, related_name='req+',
                                           null=True)
    enables = models.ManyToManyField(State, related_name='e+', null=True)
    done = models.BooleanField()
    deadline = models.DateTimeField(null=True)

    def __str__(self):
        return "{done} {name} ({proj})".format(
            name=self.name, proj=self.project,
            done=("DONE" if
                  ('done' in self.__dict__ and self.done)
                  else "    "))

    def __repr__(self):
        return "{done} {name} ({proj})".format(
            name=self.name, proj=self.project,
            done=("DONE" if self.done else "    "))


class Interval(models.Model):
    """Represents a time interval -- not just its length, but also its
    absolute position (start and end times).

    """
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)


    def clean(self):
        """Validates the object."""
        from django.core.exceptions import ValidationError
        if (self.start is not None
                and self.end is not None
                and self.end < self.start):
            self.end = self.start
            raise ValidationError('Start must be earlier than end.')

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

    class Meta:
        abstract = True


class WorkSlot(Interval):
   """ This shall be a time span (or `timedelta' in Python terminology) with
   the annotation saying how it was spent. It shall link to the relevant task
   (or, perhaps, a list of concurrently performed tasks). The annotations
   should include facts like start time, end time, concentration devoted to
   the task (may be in relation to the number of simultaneously performed
   tasks), comments, state of the task before and after this work slot.

   """
   task = models.ForeignKey(Task)

   def __str__(self):
       return "<WorkSlot: {task}, {invl}>".format(
           task=self.task,
           invl=super(WorkSlot, self).__str__())

   def __repr__(self):
       return self.__str__()
