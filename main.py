#!/usr/bin/env python3
"""
This script downloads X amount of images from a
selected subreddit. The subreddit can be specified
in the user config section of this srcipt or as
a parameter in the script.

Run example: python getWalls.py earthporn
"""

import os
from os.path import expanduser
import sys
import urllib
import requests
from PIL import ImageFile

from constants import DIRECTORY
from constants import SUBREDDIT
from constants import MIN_WIDTH
from constants import MIN_HEIGHT
from constants import JSONLIMIT
from constants import LOOPS

from constants import DARK
from constants import RED
from constants import GREEN
from constants import ORANGE
from constants import PURPLE
from constants import NC


def valid_url(url):
    """
    Returns false on status code error
    """
    try:
        status_code = requests.get(url,
                                   headers={'User-agent':'getWallpapers'}
                                   ).status_code
        if status_code == 404:
            return False

        return True
    except:
        return False


def prepare_directory(directory):
    """
    Creates download directory if needed
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print('Created directory {}'.format(directory))


def verify_subreddit(subreddit):
    """
    Returns false if subreddit doesn't exist
    """
    url = 'https://reddit.com/r/{}.json'.format(subreddit)
    try:
        requests.get(url, headers={'User-agent':'get_wallpapers'}).json()
        return True
    except:
        return False


def get_posts(subreddit, loops, after):
    """
    Returns list of posts from subreddit as json
    """
    all_posts = []

    i = 0
    while i < loops:
        url = 'https://reddit.com/r/{}/top/.json?t=all&limit={}&after={}'\
            .format(subreddit, JSONLIMIT, after)
        posts = requests.get(url,
                             headers={'User-agent':'getWallpapers'}
                             ).json()
        # allPosts.append(posts['data']['children'])
        for post in posts['data']['children']:
            all_posts.append(post)
        after = posts['data']['after']
        i += 1

    return all_posts


def is_img(url):
    """
    Returns false if URL is not an image
    """
    if url.endswith(('.png', '.jpeg', '.jpg')):
        return True
    return False


def is_hd(url, min_width, min_height):
    """
    Returns false if image from URL is not HD (Specified by min-/max_width)
    """
    file = urllib.request.urlopen(url)
    size = file.headers.get("content-length")
    if size:
        size = int(size)
    parser = ImageFile.Parser()

    while 1:
        data = file.read(1024)
        if not data:
            break
        parser.feed(data)
        if parser.image:
            # return p.image.size
            if parser.image.size[0] >= min_width and parser.image.size[1] >= min_height:
                return True
            return False

    file.close()
    return False


def is_landscape(url):
    """
    Returns false if image from URL is not landscape
    """
    file = urllib.request.urlopen(url)
    size = file.headers.get("content-length")
    if size:
        size = int(size)
    parser = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        parser.feed(data)
        if parser.image:
            # return p.image.size
            if parser.image.size[0] >= parser.image.size[1]:
                return True
            return False

    file.close()
    return False


def already_downloaded(url):
    """Returns true if image from URL is already downloaded"""
    img_name = os.path.basename(url)
    local_file_path = os.path.join(DIRECTORY, img_name)

    if os.path.isfile(local_file_path):
        return True
    return False


def known_url(post):
    """
    Returns false if image from post/URL is not from reddit or imgur domain
    """
    if post.lower().startswith('https://i.redd.it/')\
            or post.lower().startswith('https://i.imgur.com/'):
        return True
    return False


def store_img(post, directory):
    """
    Returns true if image from post/URL is stored locally
    """
    if urllib.request.urlretrieve(post, os.path.join(directory,
                                                     os.path.basename(post))):
        return True
    return False


def main():
    """ Print info when loop is finished"""
    # Creates directory
    directory = expanduser(DIRECTORY)
    directory = os.path.join(directory, SUBREDDIT)
    prepare_directory(directory)

    # Exits if invalid subreddit name
    if not verify_subreddit(SUBREDDIT):
        print('r/{} is not a valid subreddit'.format(SUBREDDIT))
        sys.exit()

    # For reddit pagination (Leave empty)
    after = ''

    # Stores posts from function
    posts = get_posts(SUBREDDIT, LOOPS, after)

    # For adding index numbers to loop
    index = 1

    # Counting amount of images downloaded
    download_count = 0

    # Print starting message
    print()
    print(DARK + '--------------------------------------------' + NC)
    print(PURPLE + 'Downloading to      : ' + ORANGE + DIRECTORY + NC)
    print(PURPLE + 'From r/             : ' + ORANGE + SUBREDDIT + NC)
    print(PURPLE + 'Minimum resolution  : ' + ORANGE + str(MIN_WIDTH) + 'x'\
          + str(MIN_HEIGHT) + NC)
    print(PURPLE + 'Maximum downloads   : ' + ORANGE + str(JSONLIMIT*LOOPS) \
          + NC)
    print(DARK + '--------------------------------------------' + NC)
    print()


    # Loops through all posts
    for post in posts:
        # Shortening variable name
        post = post['data']['url']
        # Skip post on 404 error
        if not valid_url(post):
            print(RED + '{}) 404 error'.format(index) + NC)
            index += 1

        # Skip unknown URLs
        elif not known_url(post):
            print(RED + '{}) Skipping unknown URL'.format(index) + NC)
            index += 1
            continue

        # Skip post if not image
        elif not is_img(post):
            print(RED + '{}) No image in this post'.format(index) + NC + NC + NC + NC)
            index += 1
            continue

        # Skip post if not landscape
        elif not is_landscape(post):
            print(RED + '{}) Skipping portrait image'.format(index) + NC)
            index += 1
            continue

        # Skip post if not HD
        elif not is_hd(post, MIN_WIDTH, MIN_HEIGHT):
            print(RED + '{}) Skipping low resolution image'.format(index) + NC)
            index += 1
            continue

        # Skip already downloaded images
        elif already_downloaded(post):
            print(RED + '{}) Skipping already downloaded image'.format(index) + NC)
            index += 1
            continue

        # All checks cleared, download image
        else:
            # Store image from post locally
            if store_img(post, directory):
                print(GREEN \
                    + '{}) Downloaded {}'.format(index, os.path.basename(post)) \
                    + NC)
                download_count += 1
                index += 1
            # For unexpected errors
            else:
                print(RED + 'Unexcepted error' + NC)
                index += 1


    print()
    print(ORANGE + '{}'.format(download_count) \
          + PURPLE + ' images was downloaded to ' \
          + ORANGE + '{}'.format(directory) + NC)


if __name__ == "__main__":
    main()
