#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from appdirs import user_config_dir
from configparser import ConfigParser
from os.path import join
from requests import get
from requests.auth import HTTPBasicAuth
from icalendar import Calendar as iCalendar
from icalendar import Event
from argparse import ArgumentParser
from subprocess import call


class Calendar:
    config = ConfigParser()
    configPath = join(user_config_dir('modes', 'fahrstuhl'), 'modes.ini')

    def __init__(self):
        self.refresh()

    def refresh(self):
        self.config.read(self.configPath)
        user = self.config['calendar']['username']
        link = self.config['calendar']['link']
        password = self.config['calendar']['password']
        response = get(link, auth=HTTPBasicAuth(user, password))
        self.calendar = iCalendar.from_ical(response.text)

    def create_timer_units(self):
        self.units = []
        for event in self.calendar.subcomponents:
            self.units.append(ModeTimespan(event))

    def write_timer_units(self):
        for unit in self.units:
            unit.write_timers()

#    def activate_timer_units(self):
        

    def implement(self):
        self.create_timer_units()
        self.write_timer_units()


class ModeTimespan:
    config = ConfigParser()
    configPath = join(user_config_dir('modes', 'fahrstuhl'), 'modes.ini')
    systemdUnitPath = join(user_config_dir('systemd'), 'user')
    dateTimeFormat = '%Y-%m-%d %H:%M:%S'
    filenameFormat = '%Y-%m-%d_%H-%M-%S'
    
    def __init__(self, event, name):
        self.config.read(self.configPath)
        self.event = event
        self.start = event.decoded('dtstart').strftime(self.dateTimeFormat)
        self.end = event.decoded('dtend').strftime(self.dateTimeFormat)
        self.name = event.decoded('dtstart').strftime(self.filenameFormat)
        self.unit = event.decoded('summary').decode("utf-8")
        self.startTimer = self.create_start_timer()
        self.endTimer = self.create_end_timer()

    def create_start_timer(self):
        timer = ConfigParser()
        timer.optionxform = str
        timer['Unit'] = {'Description': 'Timer to start a mode'}
        timer['Timer'] = {'OnCalendar': self.start,
                          'Unit': self.unit + "-start.service"}
        return timer

    def create_end_timer(self):
        timer = ConfigParser()
        timer.optionxform = str
        timer['Unit'] = {'Description': 'Timer to stop a mode'}
        timer['Timer'] = {'OnCalendar': self.end,
                          'Unit': self.unit + "-end.service"}
        return timer

    def write_timers(self):
        with open(join(self.systemdUnitPath, ('start' + self.name + '.timer')), 'w') as f:
            self.startTimer.write(f)
        with open(join(self.systemdUnitPath, ('end' + self.name + '.timer')), 'w') as f:
            self.endTimer.write(f)

class Task:
    def __init__(self, name):
        self.config = ConfigParser()
        self.configPath = join(user_config_dir('modes', 'fahrstuhl'), 'tasks.d', self.name + '.ini')
        self.config.read(self.configPath)
        self.doCommand = self.get_command(self.config['Task']['do'])
        self.undoCommand = self.get_command(self.config['Task']['undo'])
        try:
            self.refreshCommand = self.get_command(self.config['Task']['refresh'])
        except KeyError, e:
            self.refreshCommand = None

    def get_command(self, string):
        command = string.split()
        return command

    def do(self):
        call(self.doCommand)

    def refresh(self):
        if self.refreshCommand:
            call(self.refreshCommand)


    def undo(self):
        call(self.undoCommand)

if __name__ == "__main__":
    parser = ArgumentParser(description='Download and create work schedule')
    schedule = Calendar()
    schedule.implement()

