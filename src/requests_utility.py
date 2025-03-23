from scrape import find_content
import requests
from bs4 import BeautifulSoup
import global_variables as gv

# print() and type() are very useful in debugging
def request_function(url_passed: str) -> None:

    resp = ""
    open_sites_list = [True for site in gv.open_sites if site in url_passed]
    print(open_sites_list)
    if True in open_sites_list:
        resp = requests.get(url_passed)
    #elif [True for site in cookie_sites if site in url_passed]:
    if resp and resp.status_code == 200: # short circ eval to avoid calling on None
        print("Successfully opened the web page")
        # print(pd.read_html(url_passed))
        soup = BeautifulSoup(resp.text, 'html.parser')
        if find_content(url_passed, soup) == -1:
            return -1
    return None