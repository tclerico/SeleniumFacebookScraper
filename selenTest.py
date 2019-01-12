from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import sys
import os


def open_facebook():
    #Logs into facebook

    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # opens and logs into facebook
    driver.get("https://www.facebook.com/")
    assert "Facebook" in driver.title
    email = driver.find_element_by_id("email")
    passwd = driver.find_element_by_id("pass")

    # --------------------------------------------------

    # use your email & password !!!here they are set as environment variables!!!

    email.send_keys(os.environ.get("EMAIL"))
    passwd.send_keys(os.environ.get("PASSWORD"))
    passwd.send_keys(Keys.RETURN)

    # ----------------------------------------------------

    # opens event search page where search=music
    driver.get("https://www.facebook.com/events/discovery/?suggestion_token=%7B%22city%22%3A%22default_112943832054341%22%2C%22event_categories%22%3A[%221821948261404481%22]%7D&acontext=%7B%22ref%22%3A51%2C%22source%22%3A2%2C%22source_dashboard_filter%22%3A%22discovery%22%2C%22action_history%22%3A%22[%7B%5C%22surface%5C%22%3A%5C%22discover_filter_list%5C%22%2C%5C%22mechanism%5C%22%3A%5C%22surface%5C%22%2C%5C%22extra_data%5C%22%3A%7B%5C%22dashboard_filter%5C%22%3A%5C%22discovery%5C%22%7D%7D]%22%2C%22has_source%22%3Atrue%7D")
    return driver

def search_city(driver, city):

    more = driver.find_elements_by_class_name("_47ni")
    more[1].click()

    input = driver.find_element_by_class_name("_58al")

    input.send_keys(city)

    # wait for drop down to load
    time.sleep(2)

    # select first option in drop drop down
    input.send_keys(Keys.ARROW_DOWN)
    input.send_keys(Keys.RETURN)


def get_event_info(driver):
    # wait for page to load
    time.sleep(2)

    # get page url
    url = driver.current_url

    # get performers name(s)
    #TODO make a better way to get the artists names -> if multiple
    artists = find_artists(driver)

    # get event name
    div = driver.find_element_by_css_selector("div[class^=_5g")
    event_name = div.find_element_by_tag_name('h1')

    # get list of event info
    infolist = driver.find_element_by_id("event_summary")
    items = infolist.find_elements_by_tag_name('li')
    info = []

    for i in range(len(items)):
        # date and time
        if i == 0:
            show_time = items[0].find_element_by_css_selector("div[class^=_xk")
            info.append(show_time.find_element_by_tag_name('div'))
        # Venue
        if i == 1:
            location_div = items[1].find_element_by_css_selector("div[class^=_xk")
            inf = location_div.find_elements_by_css_selector("*")
            info.append(inf[0].text)
            info.append(inf[1].text)
        # Ticket link
        if i == 2:
            try:
                tickets = items[2].find_element_by_tag_name('a')
                ref = tickets.get_attribute('href')
                info.append(ref)
            except:
                print('blank entry')
        # ticket link if there is an extra spot
        if i == 3:
            try:
                tickets = items[3].find_element_by_tag_name('a')
                ref = tickets.get_attribute('href')
                info.append(ref)
            except:
                print('blank entry')

    # format data into dict
    if len(info) > 3:
        event_info = {
            'name': event_name.text,
            'artist(s)': artists,
            'host': info[1],
            'address': info[2],
            'time': info[0].text,
            'tickets': info[3],
            'url': url
        }
    else:
        event_info = {
            'name': event_name.text,
            'artist(s)': artists,
            'host': info[1],
            'address': info[2],
            'time': info[0].text,
            'tickets': 'N/A',
            'url': url
        }

    return event_info


def work_page(driver):
    info = []
    page_links = driver.find_elements_by_class_name("_7ty")
    for e in range(0, len(page_links)):
        links = driver.find_elements_by_class_name("_7ty")
        print("Clicking element " + str(e))
        links[e].click()
        info.append(get_event_info(driver))
        driver.back()
        time.sleep(3)

    print(info)


def find_artists(driver):
    # get large div
    div = driver.find_element_by_css_selector("div[class^=_5g")
    # get smaller div with necessary info
    info_div = div.find_element_by_css_selector("div[class^=_5g")
    nameLinks = info_div.find_elements_by_tag_name('a')

    # place all text into list
    artists = []
    for n in nameLinks:
        artists.append(n.text)

    if len(nameLinks) > 1:
        try:
            extras = nameLinks[len(nameLinks)-1].get_attribute('data-tooltip-content')
            # remove item in last 'x more'
            del artists[-1]
            # add extra artists to list
            for e in extras.splitlines():
                artists.append(e)
            return artists
        except:
            print('No Extra Artists')
    else:
        return artists


def main():
    info = []
    facebook = open_facebook()
    time.sleep(2)
    # search_city(facebook, "New Brunswick, New Jersey")
    work_page(facebook)






main()