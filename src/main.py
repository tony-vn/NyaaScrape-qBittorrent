import requests
import sys
import bs4
from bs4 import BeautifulSoup
from requests_utility import *
from os_utility import is_downloaded
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import global_variables as gv

arguments_cleaned = [arg for arg in sys.argv[1:] if not arg.startswith('--')]  # remove flags

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
# suppress annoying handshake failed ssl error msgs
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)

def load_js(url_passed: str) -> bs4.BeautifulSoup:
    driver.get(url_passed)
    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')

def is_executable():
    # print("sys.argv[0] = " + sys.argv[0])
    # print("sys.argv[1] = " + sys.argv[1])
    # print("sys.argv[2] = " + sys.argv[2])
    # print("sys.argv[3] = " + sys.argv[3])
    # print("sys.argv[4] = " + sys.argv[4])
    # print("sys.argv[5] = " + sys.argv[5])
    # print("sys.argv[6] = " + sys.argv[6])
    # check if the program is being used as an executable
    # print("len(arguments_cleaned) = " + str(len(arguments_cleaned)))
    if '.py' in sys.argv[0][-3:]: # check that the six arguments are consistent with gindfr
        # if len(arguments_cleaned[1]) == 40 and arguments_cleaned[1].isalnum() and '/' in arg[] or '\\' in arg:
            # return True
        # print("is_executable = True")
        return False
    # print("is_executable = False")
    return True

def find_url(infohash):
    # print("testing, this is the infohash for the script version: " + infohash)
    # 3 attempts at finding the nyaa url: 1) animetosho; 2) google search result page 1; 3) nyaa
    url = ""
    if not gv.open_sites[0] in url:
        found_nyaa = False
        print("Trying animetosho")
        url = "https://animetosho.org/view/{string}".format(string=infohash)  # use animetosho search algorithm
        response = requests.get(url)
        if response.history:
            print("Request redirected")
            for resp in response.history:
                print(resp.status_code, resp.url)
            print("Final destination: ")  # reached the end of redirects
            print(response.status_code, response.url)
            if response.status_code == 200:
                url = response.url
                content = requests.get(url, headers)
                soup = BeautifulSoup(content.text, "html.parser")
                first_links = [link.get("href") for link in
                               soup.find_all('a')]  # calling link['href'] errors if href is not defined in the tag
                for link in first_links:
                    if link is not None and gv.open_sites[0] in link:  # short circ eval in case of a value from get(key) returns none
                        found_nyaa = True
                        url = link
                        break
                if found_nyaa:
                    check_nyaa_resp = requests.get(link)  # check if the original nyaa page is still up
                    if check_nyaa_resp.status_code == 404:  # not up, get cache page
                        print("404 nyaa.si page through animetosho")
                        first_links2 = [link.get("href") for link in soup.find_all('a')]
                        for i in range(0, len(first_links2)):
                            if gv.open_sites[1] in first_links2[i]:
                                url = first_links2[i]
                                break
                print(url)
            else:
                url = ""
    if (not gv.open_sites[0] in url and not gv.open_sites[1] in url) or requests.get(url, headers).status_code == 404:
        print("Trying google search \n")
        url = "https://www.google.com/search?q={string}&sca_upv=1&uact=5".format(string=infohash)
        content = requests.get(url, headers=headers)
        soup = BeautifulSoup(content.text, "html.parser")
        page = soup.find(id='search')
        if page is not None:
            first_links = [link['href'] for link in page.find_all('a')]
            for link in first_links:
                if gv.open_sites[0] in link:
                    url = link
                    break
        else:
            print("Google page is NoneType\n")
    if not gv.open_sites[0] in url and not gv.open_sites[1] in url or requests.get(url, headers).status_code == 404:
        print("Trying Nyaa search\n")
        url = "https://nyaa.si/?f=0&c=0_0&q={string}".format(string=infohash)
        response = requests.get(url)
        if response.history:
            print("Request redirected")
            for resp in response.history:
                print(resp.status_code, resp.url)  # print each redirect page status_code and its url
            print("Final destination: ")  # reached the end of redirects
            print(response.status_code, response.url)
            if response.status_code == 200:  # final destination check
                url = response.url
                print(url)
            else:
                url = ""
    if not url and not "https" in sys.argv[1]:  # if url was not passed as arg 1
        print("URL not found\nEnding program or going next\n")
        # sys.exit(0)
    # flags
    if not is_downloaded(str(url)):  # will execute (download) for flags --no-list or --update if it isn't already on list i.e. not downloaded so make request
        print("Requesting URL: " + str(url))
        request_function(str(url))
    elif gv.global_flags['--update'] or gv.global_flags['--no-list']:  # ignore list, make request
        request_function(str(url))
    else:
        print("Already downloaded, skipping: " + url)

# --update: if on list, don't add to list, and write new text file; else add to list and write new text file
def main():
    # add flags
    flags = []
    for element in sys.argv[1:]:
        if element[0:2] == '--':
            flags.append(element[:].lower())
    # print(flags)
    # set flags to true
    for flag in flags: # set flags to true
        if gv.global_flags.get(flag) is False:
            gv.global_flags[flag] = True
    # print(gv.global_flags)
    # this needs a rework with new argument changes
    # for arg in sys.argv[1:len(sys.argv)-len(flags)]: # don't treat options as urls
    if not is_executable() and not gv.global_flags['--infohash']:
        for i in range(1, len(sys.argv)):
            if sys.argv[i][0:2] != '--' and sys.argv[i].isalnum() and len(sys.argv[i]) == 40: # process argument only if it is not a flag (infohash)
                infohash = sys.argv[i]
                print("This is an infohash: " + infohash)
                find_url(infohash)
            else:
                print(sys.argv[i] + " is not an infohash. Skipping.")
    elif not is_executable() and gv.global_flags['--infohash']:
        try:
            infohash_textfile = open("infohash.txt", "r")
            for infohash in infohash_textfile:
                find_url(infohash)
            infohash_textfile.close()
        except FileNotFoundError as e:
            print(e)
            try:
                print("Creating empty infohash file")
                infohash_textfile = open("infohash.txt", "x")
                exit()
            except Exception as e:
                print(e)
    elif is_executable():
        infohash = sys.argv[2]
        find_url(infohash)

    driver.close()
    driver.quit()
    return 0


if __name__ == '__main__':
    # if not "new prio" in sys.argv[1]:
    #      sys.exit(1)
    main()
