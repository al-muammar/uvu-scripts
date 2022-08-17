import json
import logging

import click
import requests

logger = logging.getLogger("gocli")


@click.group()
def gocli():
    pass


# TODO: Use disk cache to avoid hitting API too frequently
@gocli.command()
@click.option("--api-key", "-a", required=True, type=str)
@click.option("--fnin", required=True, type=str)
@click.option("--fnout", required=True, type=str)
def geocode(api_key, fnin, fnout):
    coordinates = {}
    with open(fnin) as fin:
        for line in fin.readlines():
            line = line.strip()
            address = "+".join(line.split())
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}&language=ru"
            )
            if response.status_code == requests.codes.ok:
                geocoded_results = response.json().get("results", None)
                if not geocoded_results:
                    # logger.warning(f"API returned empty results for [{line}]")
                    coordinates[line] = {"lat": None, "lon": None}
                else:
                    location = geocoded_results[0]["geometry"]["location"]
                    coordinates[line] = {"lat": location["lat"], "lon": location["lng"]}
            else:
                logger.error(
                    f"API returned {response.status_code}, message: {response.text}"
                )
                coordinates[line] = {"lat": None, "lon": None}

    with open(fnout, "w") as fout:
        json.dump(coordinates, fout, indent=2)


if __name__ == "__main__":
    gocli()
