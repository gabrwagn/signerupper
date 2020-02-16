import datetime
import settings


def try_parse_day(day):
    """
    Tries to parse the input as a weekday, if it fails it just returns the input unchanged
    :param day:
    :return:
    """
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    day_index = -1
    for i, weekday in enumerate(days):
        if day[0:3].lower() in weekday[0:3]:  # Allow matching first 3 letters: mon, tue, wed etc
            day_index = i
    if day_index == -1:
        return day

    today_index = datetime.date.today().weekday()
    day_delta = day_index - today_index

    if day_delta <= 0:
        day_delta += 7

    date = datetime.date.today() + datetime.timedelta(days=day_delta)
    return date.strftime(settings.DATE_FORMAT)


def is_valid_date_time(date, time):
    full_date = date + " " + time
    try:
        datetime.datetime.strptime(full_date, settings.DATE_TIME_FORMAT)
        return True
    except ValueError:
        return False


def is_valid_date(date):
    try:
        datetime.datetime.strptime(date, settings.DATE_FORMAT)
        return True
    except ValueError:
        return False


def is_valid_time(time):
    try:
        datetime.datetime.strptime(time, settings.TIME_FORMAT)
        return True
    except ValueError:
        return False


def is_date_time_expired(date, time):
    date = datetime.datetime.strptime(f"{date} {time}", settings.DATE_TIME_FORMAT)

    return date < datetime.datetime.now()


def parse_date_time_str(time_str):
    return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

