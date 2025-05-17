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
    display = get_display(visible)
    target_dir = './source'
    os.makedirs(target_dir, 493, True)
    mode = default_input('Start mode (t, m, f)', 'f')
    start_year = int(default_input('Start year', year - 10))
    end_year = int(default_input('End year', year))
    names = dict()
    total = 0
    with display:
        with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
            for tmp_year in range(start_year, end_year + 1):
                for page in range(1, 51):
                    if os.path.exists(f'{target_dir}/{tmp_year}_{mode}_{page}.html'):
                        with open(f'{target_dir}/{tmp_year}_{mode}_{page}.html', 'r') as f:
                            html = f.read()
                    else:
                        driver.get(f'https://www.namechart.kr/chart/{tmp_year}?gender={mode}&page={page}')
                        driver = wait_driver(driver)
                        html = driver.page_source
                        with open(f'{target_dir}/{tmp_year}_{mode}_{page}.html', 'w') as f:
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
    max_num = len(f'{sorted_names[0][1]:,}')
    max_num = 5 if max_num < 5 else max_num
    output = f'| rank | name | {"count":>{max_num}} | percent |'
    print(output)
    with open(f'{mode}_{start_year}_{end_year}.listing', 'w') as f:
        f.write(output + '\n')
    for i, (name, num) in enumerate(sorted_names, start=1):
        if num < total // 1000:
            break
        len_name = 2 if len(name) == 2 else 3
        output = f'| {i:>4} | {name:<{len_name}} | {num:>{max_num},} | {num / total:>7.2%} |'
        print(output)
        with open(f'{mode}_{start_year}_{end_year}.listing', 'a') as f:
            f.write(output + '\n')
    output = f'Total: {total:,}'
    print(output)
    with open(f'{mode}_{start_year}_{end_year}.listing', 'a') as f:
        f.write(output + '\n')


if __name__ == "__main__":
    visible = False
    if '-v' in sys.argv:
        visible = True
    main(visible)
