import datetime
from dateparser import parse
import pytz
import threading
import astral.sun
import re

import stimulus.device as device


class clock(device.device):
    def __init__(self, config):
        super().__init__()
        self.at = device.stimulator(self._register_at, self._cancel_at)
        self.datetime = device.user_function(self.get_datetime)

        self._tz = pytz.timezone(config["timezone"])
        self._timer_dict = dict()
        if not all(k in config for k in ("lat", "lon")):
            config["lat"] = 0
            config["lon"] = 0
        if "elevation" not in config:
            config["elevation"] = 0
        self._astral_obs = astral.Observer(
            config["lat"], config["lon"], config["elevation"]
        )

    def start(self):
        pass

    def get_datetime(self):
        """Get the datetime with timezone"""
        return datetime.datetime.now(self._tz)

    def _register_at(self, action, *args, **kwargs):
        # allow the user to use time (day) or times (days) in the options,
        # we'll just use kargs['times'] and kargs['days']

        if "time" in kwargs:
            kwargs["times"] = kwargs["time"]
        if "day" in kwargs:
            kwargs["days"] = kwargs["day"]

        next_func = None
        # user provides times of day to run
        if "times" in kwargs:
            kwargs["times"] = kwargs["times"].lower()
            # if no day(s) set then set to every day
            if "days" not in kwargs:
                kwargs["days"] = "Mon,Tue,Wed,Thu,Fri,Sat,Sun"
            next_func = self._recurring_days_times_func(kwargs["days"], kwargs["times"])

        # User provides their own nextTime() function
        elif "nextFunc" in kwargs:
            next_func = kwargs["nextFunc"]
        elif "countdown" in kwargs:
            if "recurring" not in kwargs:
                kwargs["recurring"] = True
            next_func = self._countdown_func(kwargs["countdown"], kwargs["recurring"])
        else:
            self.logger.warning(
                "Failed to register timer callback becuase the type isn't recognized."
            )
            return False

        # register the function.
        dt = self._get_timer_dt(next_func())
        t = threading.Timer(dt, self._get_timer_callback(next_func, action))
        t.start()
        self._timer_dict[action] = t

    def _cancel_at(self, action):
        self._timer_dict[action].cancel()
        self._timer_dict.pop(action)

    def _get_timer_callback(self, next_func, action):
        def timer_callback():
            next_date_time = next_func()
            if next_date_time is None:  # don't run next timer and delete this callback
                action.trigger({}, deleteWhenDone=True)
                self.logger.debug("Timer callback done")
            else:
                dt = self._get_timer_dt(next_date_time)
                t = threading.Timer(dt, self._get_timer_callback(next_func, action))
                t.start()
                self._timer_dict[id] = t
                self.logger.debug(f"Timer started. time: {dt}")
                action.call({})

        return timer_callback

    def _recurring_days_times_func(self, days, times):
        """Create a function that continously returns the next day/time from a comma seperated list of days and times"""
        date_time_list = list()
        now = datetime.datetime.now(self._tz)
        for day in days.split(","):
            date = parse(day)
            if date is None:
                self.logger.error(
                    f"String for recurring event on day: {day} not recognized."
                )
                continue

            for time in times.split(","):
                d = date.date()
                if self._tz.localize(self._get_date_time(d, time)) < now:
                    d = d + datetime.timedelta(weeks=1)
                date_time_list.append((d, time))

        def next_func():
            nonlocal date_time_list
            next_date_time_list = list()
            for d, t_str in date_time_list:
                next_date_time_list.append(self._get_date_time(d, t_str))

            next_date_time = min(next_date_time_list)
            next_index = next_date_time_list.index(next_date_time)
            date_time_list[next_index] = (
                date_time_list[next_index][0] + datetime.timedelta(weeks=1),
                date_time_list[next_index][1],
            )
            return next_date_time

        return next_func

    def _get_date_time(self, d, t_str):
        t_str = self._parse_solar_time(d, t_str)
        t = parse(t_str)
        if t is None:
            return None
        return datetime.datetime.combine(d, t.time())

    def _parse_solar_time(self, d, t_str):
        astral_times = astral.sun.sun(self._astral_obs, d)

        for event in astral_times:
            t_str = t_str.replace(
                event,
                astral_times[event].astimezone(self._tz).strftime("%I:%M:%S%p").lower(),
            )
        return t_str

    def _get_timer_dt(self, next):
        if next is None:
            dt = None
        elif type(next) is datetime.datetime:
            if next.tzinfo is None or next.tzinfo.utcoffset(next) is None:  # TZ Naive
                next = self._tz.localize(next)
            # calculate dt between now and next
            dt = (next - datetime.datetime.now(self._tz)).total_seconds()
        elif type(next) is int:
            dt = next
        return dt

    def _countdown_func(self, countdown, recurring):
        next_time = datetime.datetime.now(self._tz)
        delta_time = parse_time_delta(countdown)

        def next_func():
            nonlocal next_time
            nonlocal delta_time
            next_time = next_time + delta_time
            return next_time

        return next_func


def parse_time_delta(s):
    """Create timedelta object representing time delta
       expressed in a string

    Takes a string in the format produced by calling str() on
    a python timedelta object and returns a timedelta instance
    that would produce that string.

    Acceptable formats are: "X days, HH:MM:SS" or "HH:MM:SS".
    """
    if s is None:
        return None
    d = re.match(
        r"((?P<days>\d+) days, )?(?P<hours>\d+):" r"(?P<minutes>\d+):(?P<seconds>\d+)",
        str(s),
    ).groupdict(0)
    return datetime.timedelta(**dict(((key, int(value)) for key, value in d.items())))
