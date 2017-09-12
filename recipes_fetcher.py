import time
import signal
import requests
import feedparser
import json
from bs4 import BeautifulSoup, NavigableString

from selenium import webdriver
from database_handler import save_recipe, does_recipe_exist
from utils import DownloadException, TimeoutException, _timeout
from ingredient import Ingredient, Ustensile



user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/55.0.2883.87 Safari/537.36'}


def strip_tags(soup, invalid_tags):
    # soup = BeautifulSoup(str(html), 'lxml')

    for tag in invalid_tags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()

    return soup.get_text()


# 'blah blah  bleh bleh blah  ' -> 'blah blah bleh bleh blah '
def remove_spaces(s):
    if s is None:
        return ''
    if len(s) == 0:
        return ''
    s = s.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').replace('\n\xa0', ' ')
    s_new = ''
    for i in range(0, len(s) - 1):
        if not (s[i] == ' ' and s[i + 1] == ' '):
            s_new += s[i]
    return (s_new + s[-1]).strip()


def retrieve_recipe(html, recipe=None):

    if recipe is None:
        recipe = dict()

    soup = BeautifulSoup(html, 'lxml')

    # Ingredients
    recipe['ingredients'] = []
    ingredients_tags = soup.findAll('li', { "class" : "recipe-ingredients__list__item" })
    for ingredient_tag in ingredients_tags:
        ingredient_img_url = ingredient_tag.img['src']
        quantity = ingredient_tag.div.findAll('span')[0].get_text()
        complement = ingredient_tag.div.findAll('span')[1].get_text()
        [s.extract() for s in ingredient_tag('span')]

        ingredient_name = ingredient_tag.get_text()
        ingredient_name = ingredient_name.replace('&nbsp;', ' ').replace('\'', '&quot;').replace('"', '&quot;')
        ingredient_name = remove_spaces(ingredient_name)

        if ' de ' in ingredient_name or 'd&quot;' in ingredient_name:
            index_1 = ingredient_name.find(' de ')
            index_2 = ingredient_name.find('d&quot;')

            if index_1 == -1 or (index_1 != -1 and index_2 != -1 and index_2 < index_1):
                s = 'd&quot;'
            else:
                s = ' de '

            t = ingredient_name.split(s)
            quantity_name = t[0].strip()
            ingredient_name = ' '.join(t[1:]).strip()


        else:
            quantity_name = ''

        ingredient = Ingredient(name=ingredient_name, quantity_names=[quantity_name], complements=[complement])

        recipe['ingredients'].append(ingredient)

    # Ustensiles
    recipe['ustensiles'] = []
    ustensiles_tags = soup.findAll('li', { "class" : "recipe-utensils__list__item" })
    for ustensile_tag in ustensiles_tags:
        ustensile_img_url = ustensile_tag.img['src']
        ustensile_info = ustensile_tag.span.get_text()
        quantity = ustensile_info.split()[0]
        ustensile_name = ustensile_info.split()[1]

        ustensile = Ustensile(ustensile_name)

        recipe['ustensiles'].append(ustensile)

    # Steps
    recipe['steps'] = []
    steps_tags = soup.findAll('li', { "class": "recipe-preparation__list__item" })
    for step_tag in steps_tags:
        step_name = step_tag.h3.get_text()
        [s.extract() for s in step_tag('h3')]
        if step_tag is not None:
            step_content = remove_spaces(strip_tags(step_tag, ['a', 'html', 'body', 'li']))
        else:
            step_content = ''
        recipe['steps'].append({'name': step_name, 'content': step_content.replace('\'', '&quot;').replace('"', '&quot;')})

    # Duration
    recipe['duration'] = {'preparation': '0 min', 'baking': '0'}

    preparation_tag = soup.find('div', {'class': 'recipe-infos__timmings__preparation'})
    if preparation_tag is not None:
        preparation_time_tag = preparation_tag.find('span', {'class': 'recipe-infos__timmings__value'} )
        if preparation_time_tag is not None:
            preparation_time = preparation_time_tag.get_text()
            recipe['duration']['preparation'] = remove_spaces(preparation_time)

    baking_tag = soup.find('div', {'class': 'recipe-infos__timmings__cooking'})
    if baking_tag is not None:
        baking_time_tag = baking_tag.find('span', {'class': 'recipe-infos__timmings__value'} )
        if baking_time_tag is not None:
            baking_time = baking_time_tag.get_text()
            recipe['duration']['baking'] = remove_spaces(baking_time)

    # How many persons ?
    recipe['quantity'] = {'quantity': '0', 'unit': 'persons'}

    quantity_tag = soup.find('div', {'class': 'recipe-infos__quantity'} )
    if quantity_tag is not None:
        unit_tag = quantity_tag.find('span', {'class': 'recipe-infos__item-title'})
        if unit_tag is not None:
            recipe['quantity']['unit'] = unit_tag.get_text()

        quantity_tag_2 = quantity_tag.find('span', {'class': 'title-2 recipe-infos__quantity__value'})
        if quantity_tag_2 is not None:
            recipe['quantity']['quantity'] = quantity_tag_2.get_text()

    # Difficulty
    recipe['difficulty'] = '-1'

    difficulty_tag = soup.find('div', {'class': 'recipe-infos__level'} )
    if difficulty_tag is not None:
        difficulty_tag_2 = difficulty_tag.find('div', {'class': 'recipe-infos__item-title'} )
        if difficulty_tag_2 is not None:
            recipe['difficulty'] = difficulty_tag_2.get_text()

    # Price
    recipe['price'] = '-1'

    price_tag = soup.find('div', {'class': 'recipe-infos__budget'} )
    if price_tag is not None:
        price_tag_2 = price_tag.find('div', {'class': 'recipe-infos__item-title'} )
        if price_tag_2 is not None:
            recipe['price'] = price_tag_2.get_text()

    return recipe


# Retrieve the html and the url after redirection of a given url
# There are a lot of exceptions to handle there..
def get_html(url, timeout_seconds=20):
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(timeout_seconds)

    verbose = False

    try:  # sometimes the async SIGALRM signal is called outside of the inner try/except
        try:  # force timeout of the request
            resp = requests.get(url, allow_redirects=True, headers=user_agent)
        except TimeoutException:
            if verbose: print('Request timed out:', url)
            raise DownloadException('timeout')
        except Exception as e:  # an exception from requests lib
            if verbose: print('\'{}\' exception retrieving URL \'{}\': {}'.format(type(e), url, e))
            raise DownloadException('unknown exception', {'exception': e})
        else:
            if not resp.ok:  # content fetched without any exception but error code
                if verbose: print('Bad status code for URL \'{}\': {}'.format(url, resp.status_code))
                raise DownloadException('bad status code', {'status_code': resp.status_code})
            elif not resp.headers.get('content-type', '').startswith('text/html'):  # content is not html
                if verbose: print('Not a html url:', url)
                raise DownloadException('bad content type', {'content_type': resp.headers.get('content-type', None)})
            else:  # valid response, & html file
                if 'dnserrorassist' in resp.text:  # AT&T display custom page when the url doesn't exist
                    if verbose: print('Got ATT DNS... Probably invalid URL:', url)
                    raise DownloadException('att dns error')
                else:
                    if verbose: print('Successfully fetched:', url)
                    try:
                        return resp.url, resp.content.decode('utf-8')
                    except UnicodeDecodeError:
                        # sometimes decoding with utf-8 does not work, use requests built-in instead
                        if verbose: print('Error (ignored) converting to unicode:', url)
                        return resp.url, resp.text
    except TimeoutException:
        if verbose: print('Timeout after request ended: ignore it:', url)
    finally:
        signal.alarm(0)


def rss_reader(rss_url):

    save = True

    feed = feedparser.parse(rss_url)
    url_recipe = feed['entries']

    recipes = []
    for i in range(len(url_recipe)):
        try:
            recipe = dict()
            recipe['url_original_website'] = url_recipe[i]['links'][0]['href']
            recipe['url_image_original_website'] = url_recipe[i]['links'][1]['href']
            recipe['title'] = url_recipe[i]['title_detail']['value']

            try:
                url, html = get_html(recipe['url_original_website'])
                recipe['url_original_website'] = url
                recipe['html'] = html
            except Exception as e:
                print('Exception occurred : ', e)
                save = False
                recipe['html'] = ''

            recipe = retrieve_recipe(recipe['html'], recipe=recipe)

            if save and not does_recipe_exist(recipe):
                save_recipe(recipe)
                print('#')
        except Exception as e:
            print('Exception rss_reader: ', e)


if __name__ == '__main__':
    marmiton_rss_url = 'http://www.marmiton.org/rss/recettes-au-hasard.aspx'

    for i in range(10000):
        print('Fetching a new recipe...')
        rss_reader(marmiton_rss_url)
        time.sleep(1)
