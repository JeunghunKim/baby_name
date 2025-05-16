#! /usr/bin/env python3

import os
import sys
import datetime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from pyvirtualdisplay import Display
# pip install bs4 tqdm
# pip install selenium webdriver_manager pyvirtualdisplay bs4 tqdm
# sudo apt-get install xvfb xserver-xephyr


def get_display(visible):
    if visible:
        return Display(visible=1)
    else:
        return Display(visible=0, size=(1440, 2560 * 2))


def wait_driver(driver, wait_time=60):
    WebDriverWait(driver, wait_time).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    return driver


def default_input(name, default):
    return input(f'{name} (default: {default}): ').strip() or default


def main(visible):
    year = datetime.datetime.now().date().year
    target_dir = './source'
    os.makedirs(target_dir, 493, True)
    display = get_display(visible)
    start_year = int(default_input('Start year', year - 10))
    end_year = int(default_input('End year', year))
    names = dict()
    total = 0
    with display:
        with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
            for i in range(start_year, end_year + 1):
                if os.path.exists(f'{target_dir}/{i}.html'):
                    with open(f'{target_dir}/{i}.html', 'r') as f:
                        html = f.read()
                else:
                    driver.get(f'https://www.namechart.kr/chart/{i}?gender=f')
                    driver = wait_driver(driver)
                    html = driver.page_source
                    with open(f'{target_dir}/{i}.html', 'w') as f:
                        f.write(html)
                soup = BeautifulSoup(html, 'html.parser')
                cells = soup.select('body > main > div > div > div > table > tbody > tr')
                for cell in cells:
                    name = cell.select('td')[1].text
                    num = int(cell.select('td')[2].text.replace(',', ''))
                    total += num
                    if name in names.keys():
                        names[name] += num
                    else:
                        names[name] = num
    sorted_names = sorted(names.items(), key=lambda x: x[1], reverse=True)
    for i, (name, num) in enumerate(sorted_names, start=1):
        print(f'{i} | {name}:\t{num:>6,}\t{num / total:.2%}')
    print(f'Total: {total:,}')


if __name__ == "__main__":
    visible = False
    if '-v' in sys.argv:
        visible = True
    main(visible)
