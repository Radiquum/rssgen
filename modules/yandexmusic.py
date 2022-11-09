from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnknownMethodException
from time import sleep
import logging
logger = logging.getLogger('application')
# > Release Parser:
#options.add_argument("--disable-gpu")

from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def read_cookies(p):
    cookies = []
    with open(p, 'r') as f:
        for e in f:
            e = e.strip()
            if e.startswith('#'): continue
            k = e.split('\t')
            if len(k) < 3: continue	# not enough data
            # with expiry
            cookies.append({'name': k[-2], 'value': k[-1], 'expiry': int(k[-3])})
    return cookies    
    
def fetch_new_releases(cookie_file=None, username=None, fetch=50):
    # sourcery skip: for-append-to-extend
    logger.info('---------[Updating Yandex.Music New Releases Info]---------')
    # try:
    #     from selenium.webdriver.edge.options import Options
    #     options = Options()
    #     options.page_load_strategy = 'eager'
    #     options.add_argument("--headless")
    #     driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options=options)
    # except Exception:
    #     from selenium.webdriver.firefox.options import Options
    #     options = Options()
    #     options.page_load_strategy = 'eager'
    #     options.add_argument("--headless")
    #     driver = webdriver.Firefox(GeckoDriverManager().install(), options=options)

    # from selenium.webdriver.edge.options import Options
    # options = Options()
    # options.add_argument("--headless")
    # driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options=options)

    capabilities = {
        "browserName": "firefox",
        "version": "106.0",
        "platform": "LINUX"
    }

    driver = webdriver.Remote(
       command_executor="http://rss-selenium-firefox:4444/wd/hub",
       desired_capabilities=capabilities)

    count = 0
    driver.implicitly_wait(2)
    driver.get('https://music.yandex.ru/new-releases')
    if cookie_file is not None:
        cookies = read_cookies(cookie_file)
        for c in cookies: 
            count = count + 1
            driver.add_cookie(c)
            logger.info(f'---------[added {count} cookies / {len(cookies)}]---------')

    driver.refresh()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

    elements = driver.find_elements(By.CLASS_NAME, "album")
    count = 0
    albums = []
    for x in elements:
        count = count + 1
        if count > fetch:
            continue
        logger.info(f'---------[processed {count} albums / {fetch}]---------')
        album_artists = []
        try:
            artists = x.find_element(By.CLASS_NAME, 'd-artists').find_elements(By.TAG_NAME, 'a')
            for y in artists:
                album_artists.append([y.get_attribute('title'), y.get_attribute('href')])
        except Exception:
            album_artists.append(x.find_element(By.CLASS_NAME, 'deco-typo-secondary').get_attribute('title'))
        
        albums.append([x.find_element(By.CLASS_NAME, 'entity-cover__image').get_attribute('src'), x.find_element(By.CLASS_NAME, 'album__caption').get_attribute('text'), x.find_element(By.CLASS_NAME, 'album__caption').get_attribute('href'), album_artists, x.find_element(By.CLASS_NAME, 'deco-typo-secondary').get_attribute('title')])

    logger.info('---------[Completed Yandex.Music New Releases Info Updating]---------')
    driver.quit()
    generate_new_releases_feed(username, albums)

# > Feed Generation:

import datetime
from genrss import GenRSS

def generate_new_releases_feed(username=None, df=None):
    logger.info('---------[Creating Yandex.Music New Releases Feed]---------')
    
    feed = GenRSS(title=f'Yandex Music New Releases for {username}',
              site_url='https://music.yandex.ru/new-releases',
              feed_url=f'https://python-rss.server.paws.cf/yandex-music/new-releases?username={username}')

    for album in df:
        artists = []
        for artist in album[3]:
            artists.extend([f"<a href='{artist[1]}'>{artist[0]}</a>"])
        artists = ', '.join(map(str,artists))
        
        feed.item(title=f'New Release: {album[4]} - {album[1]}',
                description=f'<img src="{album[0]}"/> <br> New Release: {artists} - <a href="{album[2]}">{album[1]}</a>',
                url=album[2],
                author=None,
                categories=[],
                pub_date=datetime.datetime.now())


    with open(f'rss/yandexmusic-{username}.xml', 'w', encoding='utf-8') as file:
        file.write(feed.xml(pretty=True))

    logger.info('---------[Completed Creating Yandex.Music New Releases Feed]---------')
