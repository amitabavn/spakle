import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from amtb_blogs.FileWriter import FileWriter


def login():
    login_url = '<HOST-URL>/login'  # Replace with the URL of the login page
    data = {
        'username': '<USERNAME>',
        'password': '<PASSWORD>'
    }
    session = requests.Session()
    session.post(login_url, data=data)
    return session


def fetch_page_content(url, session):
    # Scroll down until reaching the bottom end of the page to get full contents
    webdriver_service = Service('path/to/chromedriver')
    driver = webdriver.Chrome(service=webdriver_service)
    driver.get(url)
    response = session.get(url)
    if response.status_code == 200:
        cookies = session.cookies.get_dict()
        for cookie in cookies:
            driver.add_cookie({'name': cookie, 'value': cookies[cookie]})

        scroll_pause_time = 6
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html = driver.page_source
        driver.quit()
        return html
    else:
        print("Failed to fetch the page. Status code:", response.status_code)
        return None


def fetch_page_content(url):
    # Scroll down until reaching the bottom end of the page to get full contents
    webdriver_service = Service('path/to/chromedriver')
    driver = webdriver.Chrome(service=webdriver_service)
    driver.get(url)

    scroll_pause_time = 6
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html = driver.page_source
    driver.quit()
    return html


def parse_page_content(page_content):
    return BeautifulSoup(page_content, "html.parser")


def get_parent_topics(soup):
    parent_topics = []
    parent_topic_wrappers = soup.find_all('div', class_='topics-v2__category-wrapper')
    for parent_topic_wrapper in parent_topic_wrappers:
        parent_topic_element = parent_topic_wrapper.find('a', class_='topics-v2__topic-parent')
        if parent_topic_element is None:
            continue
        parent_topic_name = parent_topic_element.text.strip()

        sub_topics_elements = parent_topic_wrapper.find_all('a', class_='topics-v2__topic')
        sub_topic_data = [{"sub_topic_name": sub_topic.text.strip(), "sub_topic_link": sub_topic['href']}
                          for sub_topic in sub_topics_elements]

        parent_topics.append({'parent_topic_name': parent_topic_name, 'sub_topics': sub_topic_data})

    return parent_topics


def get_video_titles(soup):
    return get_titles(soup, 'tile-video', 'tile-video__title')


def get_series_titles(soup):
    return get_titles(soup, 'tile-series', 'tile-video__title')


def get_episode_titles(soup):
    episode_titles = []
    episode_title_wrappers = soup.find_all('div', class_='tile-episode')
    for episode_title_wrapper in episode_title_wrappers:
        episode_title_element = episode_title_wrapper.find('a', class_='tile-episode__title')
        series_title_element = episode_title_wrapper.find('a', class_='tile-episode__series-title')
        season = episode_title_wrapper.find('span', class_='text-season')
        episode = episode_title_wrapper.find('span', class_='text-episode')
        episode_titles.append(
            {'title': episode_title_element.text.strip(), 'link': episode_title_element['href'],
             'series': series_title_element.text.strip(), 'series_link': series_title_element['href'],
             'episode_number': season.text.strip() + ':' + episode.text.strip()})
    return episode_titles


def get_titles(soup, tile_class, title_class, extra_fields=None):
    titles = []
    title_wrappers = soup.find_all('div', class_=tile_class)
    for title_wrapper in title_wrappers:
        title_element = title_wrapper.find('a', class_=title_class)
        title = title_element.text.strip()
        link = title_element['href']
        title_dict = {'title': title, 'link': link}
        if extra_fields:
            for field in extra_fields:
                field_element = title_wrapper.find(*field['selector'])
                field_value = field_element.text.strip()
                if field.get('format'):
                    field_value = field['format'](field_value)
                title_dict[field['name']] = field_value
        titles.append(title_dict)
    return titles


class GaiaVideoTitleCrawler:
    def __init__(self):
        self.host_url = "<HOST-URL>"
        self.base_url = self.host_url + "/topics"
        self.parent_topic_info = []
        self.writer = FileWriter('../topics_videos_list.csv')

    def crawl(self):
        page_content = fetch_page_content(self.base_url)
        if not page_content:
            return

        soup = parse_page_content(page_content)
        parent_topics = get_parent_topics(soup)

        for parent_topic in parent_topics:
            if parent_topic['parent_topic_name'] in ['Yoga']:
                continue
            for sub_topic in parent_topic['sub_topics']:
                videos_list_page_content = fetch_page_content(self.host_url + sub_topic['sub_topic_link'])
                videos_list_soup = parse_page_content(videos_list_page_content)
                videos = get_video_titles(videos_list_soup)
                series = get_series_titles(videos_list_soup)
                episodes = get_episode_titles(videos_list_soup)
                sub_topic['sub_topic_videos'] = {'videos': videos, 'series': series, 'episodes': episodes}
            self.writer.write_results_to_csv(parent_topic)
        return self.parent_topic_info
