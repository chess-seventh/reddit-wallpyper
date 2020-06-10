import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Where to store downloaded images
DIRECTORY = config['Default']['directory'].replace("'", "")
# which subreddit to download from
SUBREDDIT = config['Reddit']['subs'].replace("'", "")
# minimum width of image
MIN_WIDTH = int(config['Size']['min_width'])
# minimum height of image
MIN_HEIGHT = int(config['Size']['min_height'])
# how many posts to get for each request (max 100)
JSONLIMIT = int(config['Default']['jsonLimit'])
# increase this number if the number above (jsonlimit) isn't enough posts
LOOPS = int(config['Default']['loops'])

DARK = '\033[1;30m'
RED = '\033[1;31m'
GREEN = '\033[1;32m'
ORANGE = '\033[1;33m'
PURPLE = '\033[1;35m'
NC = '\033[0m'
