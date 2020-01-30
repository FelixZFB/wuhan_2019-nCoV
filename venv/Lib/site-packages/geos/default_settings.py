"""
Default settings that will be loaded in the Flask app.config dict.
"""

# Werkzeug debugger
DEBUG = False

HOST = 'localhost'
PORT = 5000

# between 0 and 5. A higher number will put more tiles in a region, thus reducing
# the number of network links and the server load.
LOG_TILES_PER_ROW = 1

