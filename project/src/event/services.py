from datetime import datetime

from django.utils import timezone


def check_date(date):
    """
    Get the restaurant associate to the order customer

    :param date: A date in string format to check
    :type date: str
    :return: date in datetime format
    :type return: datetime.datetime
    """
    try:
        return timezone.make_aware(
            datetime.strptime(date, "%Y-%m-%d"),
            timezone.get_current_timezone()
        ).date()
    except TypeError:
        return None
    except ValueError:
        return None
