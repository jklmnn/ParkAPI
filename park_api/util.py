import pytz
from datetime import datetime

from park_api import db

LOT_COUNTS_PER_CITY = {}


def get_most_lots_from_known_data(city, lot_name):
    """
    Get the total value from the highest known value in the last saved JSON.
    This is useful for cities that don't publish
    total number of spaces for a parking lot.

    Caveats:
     - Returns 0 if not found.
     - If a lot name exists twice only the last value is returned.

    :param city:
    :param lot_name:
    :return:
    """
    global LOT_COUNTS_PER_CITY
    # FIXME ugly work around, this should be really fixed in a different way
    lot_counts = LOT_COUNTS_PER_CITY.get(city, {})
    if lot_counts == {}:
        with db.cursor() as cursor:
            sql = """
            SELECT data FROM parkapi
            WHERE city=%s
            ORDER BY timestamp_downloaded DESC LIMIT 600;
            """
            cursor.execute(sql, (city,))
            all_data = cursor.fetchall()
            for json_data in all_data:
                lots = json_data[0]["lots"]
                for lot in lots:
                    highest_count = lot_counts.get(lot_name, 0)
                    count = int(lot["free"])
                    if count > highest_count:
                        lot_counts[lot_name] = count
        LOT_COUNTS_PER_CITY[city] = lot_counts
    return lot_counts.get(lot_name, 0)


def utc_now():
    """
    Returns the current UTC time in ISO format.

    :return:
    """
    return datetime.utcnow().replace(microsecond=0).isoformat()


def convert_date(date_string, date_format, timezone="Europe/Berlin"):
    """
    Convert a date into a ISO formatted UTC date string.
    Timezone defaults to Europe/Berlin.

    :param date_string:
    :param date_format:
    :param timezone:
    :return:
    """
    last_updated = datetime.strptime(date_string, date_format)
    local_timezone = pytz.timezone(timezone)
    last_updated = local_timezone.localize(last_updated, is_dst=None)
    last_updated = last_updated.astimezone(pytz.utc).replace(tzinfo=None)

    return last_updated.replace(microsecond=0).isoformat()
