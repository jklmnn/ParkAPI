from bs4 import BeautifulSoup
from park_api.geodata import GeoData
from park_api.util import convert_date

data_url = "http://www.bcp-bonn.de/bspspinfo1.php"
data_source = "http://www.bcp-bonn.de/bcp/index.php?id=80"
city_name = "Bonn"

geodata = GeoData(__file__)

lot_map = {
        0: "Münsterplatzgarage",
        1: "Stadthausgarage",
        2: "Beethoven-Parkhaus",
        3: "Bahnhofgarage",
        4: "Friedensplatzgarage",
        5: "Marktgarage",
        }


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")

    free_lots = soup.find_all("td", {"class": "stell"})
    assert len(free_lots) == 6, "Expect to find 6 lots in Bonn, got: %d" % len(free_lots)
    time = soup.find("td", {"class": "stand"}).text.strip()

    lots = []
    for idx, free in enumerate(free_lots):
        lot = geodata.lot(lot_map[idx])
        lots.append({
            "name": lot.name,
            "coords": lot.coords,
            "free": int(free.text),
            "address": lot.address,
            "total": lot.total,
            "state": "nodata",
            "id": lot.id,
            "forecast": False
        })

    return {
        "last_updated": convert_date(time, "%d.%m.%y %H:%M:%S"),
        "data_source": data_source,
        "lots": lots
    }