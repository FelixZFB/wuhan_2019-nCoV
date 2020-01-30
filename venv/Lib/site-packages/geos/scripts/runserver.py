#!/usr/bin/env python3

"""
Start the GEOS server from command line.
"""

from geos import app
import argparse
import geos.mapsource
import pkg_resources
from geos.kml import URLFormatter

MAPSOURCES = pkg_resources.resource_filename("geos", "mapsources")

app.config.from_object('geos.default_settings')


def run_app(default_host=app.config['HOST'], default_port=app.config['PORT']):
    argp = argparse.ArgumentParser("geos")
    argp.add_argument("-m", "--mapsource", required=False,
                      default=None,
                      help="path to the directory containing the mapsource files. [default: integrated mapsources]")
    argp.add_argument("-H", "--host", required=False,
                      help="Hostname of the Flask app [default {}]".format(default_host),
                      default=default_host)
    argp.add_argument("-P", "--port", required=False,
                      help="Port for the Flask app [default {}]".format(default_port),
                      default=default_port)
    argp.add_argument("--display-host", required=False,
                      help="Hostname used for self-referencing links [defaults to Flask hostname]",
                      default=None)
    argp.add_argument("--display-port", required=False,
                      help="Port used for self-referencing links [defaults to Flask port]",
                      default=None)
    argp.add_argument("--display-scheme", required=False,
                      help="URI-scheme used for self-referencing links [default {}]".format(app.config["PREFERRED_URL_SCHEME"]),
                      default=None)

    args = argp.parse_args()

    app.config['url_formatter'] = URLFormatter(
        host=args.display_host if args.display_host else args.host,
        port=args.display_port if args.display_port else args.port,
        url_scheme=args.display_scheme if args.display_scheme else app.config["PREFERRED_URL_SCHEME"]
    )
    app.config['mapsources'] = geos.mapsource.load_maps(MAPSOURCES)
    if args.mapsource is not None:
        app.config["mapsources"].update(geos.mapsource.load_maps(args.mapsource))

    app.run(
        host=args.host,
        port=int(args.port)
    )

if __name__ == "__main__":
    run_app()
