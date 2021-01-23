"""tests/test_server.py

Tests for server.py

Total points: 100
"""

from io import StringIO
from unittest.mock import patch
from bs4 import BeautifulSoup
from flask import session
import os
import re
import pytest_check as pcheck
from pytest_check import check
import logging

# Set up logging so we can log passing tests as well as failing tests
# TODO: Colorize the logs and set up a custom format somehow for the
# HTML report.
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger()

# Useful for testing
# from IPython import embed

TEST_USER_NAME = "Test User"

def test_gitignore_exists(client):
    path_to_gitignore = os.path.join(
        os.getcwd(), 
        client.application.config['CWD'], 
        '.gitignore'
    )

    # Ensure .gitignore exists and is not empty
    with check:
        assert os.path.isfile(path_to_gitignore) and os.path.getsize(path_to_gitignore) > 0
        mylogger.info(".gitignore file exists.")

def test_homepage_h1(client):
    # TODO: Should check to see that they properly called render_template

    response = client.get('/')
    
    soup = BeautifulSoup(response.data, 'html.parser')

    # Ensure they made the h1 properly
    with check:
        assert soup.h1.text in ["UberMelon's Most Loved Melons", "UberMelon’s Most Loved Melons"]
        mylogger.info("Homepage heading is correct.")

def test_homepage_img(client):

    response = client.get('/')
    
    soup = BeautifulSoup(response.data, 'html.parser')

    # Check that there is at least one image.
    with check:
        assert len(soup.find_all('img')) >= 1
        mylogger.info("Homepage has an image.")


def test_homepage_melon_info(client):
    
    response = client.get('/')
    
    soup = BeautifulSoup(response.data, 'html.parser')

    # Ensure there is at least one form
    if pcheck.is_not_none(soup.form):
        mylogger.info("Homepage get-name form exists")

    # Check that the form's attributes are set correctly
    if pcheck.equal(soup.form.get('action'), '/get-name'): 
        mylogger.info("Action is set correctly for the get-name form")

    if pcheck.equal(soup.form.get('method', 'get').lower(), 'get'): 
        mylogger.info("Method is set correctly for the get-name form")

    if pcheck.is_not_none(soup.form.input.get('required')): 
        mylogger.info("get-name form input is marked as required")

def test_get_name(client):
    # TODO: Should check to see that they properly called render_template

    # Grab the homepage since we need the form input name
    response = client.get('/')
    soup = BeautifulSoup(response.data, 'html.parser')

    # Set the name, without following redirects
    input_name = soup.form.input.get('name')
    response = client.get(f'/get-name?{input_name}={TEST_USER_NAME}')

    # Ensure session variable gets set correctly, but we don't know the name, so we just check that one 
    # of the values matches our name
    if pcheck.is_in(TEST_USER_NAME, session.values()):
        mylogger.info("Username got stored in the session.")

    # # Ensure we are properly getting redirected
    with check:
        assert response.location.endswith('/top-melons')
        mylogger.info("While setting name, got redirected to /top-melons.")


def test_redirect_when_logged_in(client):
    # Try to go back to the homepage, now that we're "logged in"
    response = client.get('/')

    # Ensure we got redirected again
    with check:
        assert response.location.endswith('/top-melons')
        mylogger.info("Homepage properly redirects to /top-melons after setting name.")

    # FIXME: This doesn't clear the session when it's done, and so testing is not idempotent. We should
    # clear the session and set the name again in each test case so we can run the tests indidivually
    # as well as together.

def test_top_melon_greeting(client):
    # TODO: Should check to see that they properly called render_template and passed in MOST_LOVED_MELONS
    # using Jinja, and they arent hardcoding it.
    
    response = client.get('/top-melons')
    soup = BeautifulSoup(response.data, 'html.parser')

    # Ensure they greeted us.
    if pcheck.is_in(TEST_USER_NAME, soup.h1.get_text()):
        mylogger.info("/top-melons propertly greets the user")


def test_melon_images(client):
    response = client.get('/top-melons')
    soup = BeautifulSoup(response.data, 'html.parser')

    melons = soup.find_all('img')

    if pcheck.equal(len(melons), 4):
        mylogger.info("There are four images on /top-melons.")


def test_melon_greetings(client):
    response = client.get('/top-melons')
    soup = BeautifulSoup(response.data, 'html.parser')

    melons = soup.find_all('text')

    for melon in melons:
        # Ensure they greet us again, because otherwise they're still rude.
        with check:
            assert melon.h3.get_text().startswith(TEST_USER_NAME)

    mylogger.info("Melon names on /top-melons include the username.")


def test_melon_info(client):
    melon_lookup = {
        'Crenshaw': {
            'img': 'http://www.rareseeds.com/assets/1/14/DimRegular/crenshaw.jpg',
            'num_loves': 584
        },
        'Jubilee Watermelon': {
            'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Jubilee-Watermelon-web.jpg',
            'num_loves': 601
        },
        'Sugar Baby Watermelon': {
            'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Sugar-Baby-Watermelon-web.jpg',
            'num_loves': 587
        },
        'Texas Golden Watermelon': {
            'img': 'http://www.rareseeds.com/assets/1/14/DimThumbnail/Texas-Golden-2-Watermelon-web.jpg',
            'num_loves': 598
        }
    }

    response = client.get('/top-melons')
    soup = BeautifulSoup(response.data, 'html.parser')

    melons = soup.find_all('div')

    for melon in melons:
        # Get the melon name by matching a regex against the h3 in the div
        melon_name = re.search(r'this is a\s+(?P<melon_name>.*)', melon.h3.get_text()).group('melon_name')
        num_loves = int(re.search(r'\s+(?P<num_loves>\d+)\s+', melon.h2.get_text()).group('num_loves'))
        img_url = melon.img.get('src')

        # Ensure they are using our melons
    
        if pcheck.is_in(melon_name, melon_lookup.keys()):
            mylogger.info(f"{melon_name} is properly labeled on /top-melon")

        if pcheck.equal(melon_lookup[melon_name]['num_loves'], num_loves):
            mylogger.info(f"{melon_name} has the right num_loves on /top-melon")

        if pcheck.equal(melon_lookup[melon_name]['img'], img_url):
            mylogger.info(f"{melon_name} uses the correct image on /top-melon")


# TODO: Test styles, and test the optional 'love-melon' route. I don't know how to mark pytest cases as optional,
# or so they emit warnings, rather than failures, so do this at a later time.


if __name__ == "__main__":
    pytest.main()