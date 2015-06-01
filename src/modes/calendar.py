#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from appdirs import user_config_dir
from configparser import ConfigParser
from os.path import join
from requestes import get
from requests.auth import HTTPBasicAuth
from icalendar import Calendar, Event


class Calendar:
    config = ConfigParser()
    configPath = join(user_config_dir('modes', 'fahrstuhl'), 'modes.ini')

    def __init__(self):
        self.config.read(configPath)
        user = config['calendar']['username']
        link = config['calendar']['link']
        password = config['calendar']['password']
        response = get(link, auth=HTTPBasicAuth(user, password))
        self.calendar = Calendar.from_ical(response.text)

    def create_timer_units(self):
        self.units = []
        for event in self.calendar.subcomponents:
            self.units.append(create_timer_unit(each))

    def create_timer_unit(self, event):
        return unit

class ModeTimespan:
    
    config = ConfigParser()
    configPath = join(user_config_dir('modes', 'fahrstuhl'), 'modes.ini')
    systemd = ConfigParser()
    systemdUnitPath = join(user_config_dir('systemd'), 'user')
    
    def __init__(self, event):
        self.event = event
        self.start = event.decoded('dtstart').strftime(self.config['calendar']['datetimeformat'])
        self.end = event.decoded('dtend').strftime(self.config['calendar']['datetimeformat'])

    def create_start_timer(self):
        timer = ConfigParser()
        timer['Unit'] = {'Description': 'Timer to start a mode'}
        timer['Timer'] = {'OnCalendar': self.start}
        return timer

    def create_end_timer(self):
        timer = ConfigParser()
        timer['Unit'] = {'Description': 'Timer to stop a mode'}
        timer['Timer'] = {'OnCalendar': self.end}
        return timer

