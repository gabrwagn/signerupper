import datetime
import settings


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

