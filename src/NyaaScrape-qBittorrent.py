import bs4
import numpy
import requests
from bs4 import BeautifulSoup
import sys
import os
import pandas as pd
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import shutil
import re
import textwrap
import glob

download_txt_file_path = r"downloaded.txt"
download_txt_file_path = download_txt_file_path.replace(os.sep, '/')

readmes_folder_path = r"readmes"
readmes_folder_path = readmes_folder_path.replace(os.sep, '/')

# make file if it does not exist
if not os.path.exists(readmes_folder_path):
    os.makedirs(readmes_folder_path)
if not os.path.exists(download_txt_file_path):
    downloaded_list = open(download_txt_file_path, 'x', encoding="utf-8")
    downloaded_list.close()

# r for raw string; \\ interpreted as \ however since \ is the escape character in python; os.sep finds what
# your os uses to separate filenames for its path and replaces it with the char in the second argument
file_path = r"readmes\\"
file_path = file_path.replace(os.sep, '/')

global_flags = {'--no-list': False, '--write-new': False, '--update': False}

def move_file_function(file_path: str, file_name: str) -> None:
    # the strings imported from qBittorrent are automatically imported into python with appropriate escaping of chars
    # for the / eg. c:/folder is c://folder
    # G I N D F R
    # %N is just the torrent name only, no path or anything else
    # %D is the path holding the downloaded file or its subfolder if that option is selected
    # %F is the path to the singular mkv file (unsure for multipart torrent file)
    # %R is the subfolder path if that option is selected
    destination_path = sys.argv[6].replace(os.sep, '/')
    if os.path.isdir(destination_path) and sys.argv[5][-3:] == 'mkv' or sys.argv[3][-3] == 'mkv':
        file_name = file_name.replace(os.sep, '/').split('/')[-1]
        shutil.move("{}/{}".format(file_path, file_name), "{}/{}".format(destination_path, file_name))
        return None
    elif sys.argv[3][-3:] == 'mkv':  # no subfolder case
        destination_path = sys.argv[4].replace(os.sep, '/')
    else:  # original content layout folder case
        destination_path = sys.argv[5].replace(os.sep, '/')
    shutil.move("{}/{}".format(file_path, file_name), "{}/{}".format(destination_path, file_name))
    print("Logging src path and destination path respectively: '{}' '{}'".format("{}/{}".format(file_path, file_name),"{}/{}".format(destination_path,file_name)))
    return None


def write_function(trunked_title: str, body_text_html: bs4.BeautifulSoup, url_passed: str, title: str, file_title: str, soup: bs4.BeautifulSoup) -> None:
    extra_title = ""
    if "nyaa" in url_passed and not "cache" in url_passed:
        body_text_string = body_text_html.get_text(separator="\n\n") # work done in find_content function
    elif "nyaa" in url_passed and "cache" in url_passed:
        body_text_string = body_text_html # work done in find_content function
    else:
        body_text_string = body_text_html.get_text(separator="\n", strip=True)
    # flag handling
    if global_flags['--write-new'] or global_flags['--update']:
        if "nyaa" in url_passed:
            pattern = re.sub(r'([\[\]])', r'[\1]', file_path + trunked_title + extra_title) + "*.txt"
            result = glob.glob(pattern)
            new_version = len(result)
            old_name = file_path + trunked_title + extra_title + ".txt"
            new_name = file_path + trunked_title + extra_title + "v" + str(new_version) + ".txt"
        else:
            pattern = re.sub(r'([\[\]])', r'[\1]', (file_path + trunked_title + extra_title)) + "*.txt"
            result = glob.glob(pattern)
            # the new version number is just the length of the list returned by glob
            new_version = len(result)
            # the old name is the current name
            old_name = file_path + trunked_title + extra_title + ".txt"
            # the new name is the file name with v literal and the version number added
            # python quirk: if you add an int at the end, python expects ints for subsequent concats
            new_name = file_path + trunked_title + extra_title + "v" + str(new_version) + ".txt"
        try:
            # use the os module to rename the file from old to new
            os.rename(old_name, new_name)
        except FileNotFoundError as e:
            print("Warning: ", e, end="")
            print("\nWriting a new file")
        except WindowsError as e:
            print("Warning:", e, "for", url_passed, "exiting", end="")
            exit()
        except:
            print("An unexpected error occurred for " + url_passed + " exiting")
            exit()
    if "nyaa" in url_passed and not "cache" in url_passed:
        # scrape ALL comments
        nyaa_comments_string = "COMMENTS:\n"
        # find consistent patterns in order to find relevant html elements we can extract our data from
        for comment in soup.findAll("div", attrs={'class': 'panel panel-default comment-panel'},id=re.compile('com-[0-9]')):  # re.compile is just regex
            username = comment.find("a",class_=re.compile('text-')).get_text()  # get_text() gets text that a tag encloses
            nyaa_comments_string += username + "\n"
            date = comment.find("small").get("title")
            nyaa_comments_string += date + "\n"
            user_blockquote = comment.find("div", class_="comment-content").find("blockquote") # May return a NoneType if it does not exist
            if not user_blockquote is None: # handling blockquotes such that it's clear that the comment is responding to someone else. Must first check type
                user_blockquote = user_blockquote.get_text().strip()
                nyaa_comments_string += "\"" + user_blockquote + "\"\n"
                comment.find("div", class_="comment-content").blockquote.extract() # delete the tag and its contents to avoid dupe
            user_comment = comment.find("div", class_="comment-content").get_text().strip()
            nyaa_comments_string += user_comment + "\n\n"
        f = open(file_path + trunked_title + extra_title + ".txt", "x", encoding="utf-8")
        f.write(title + "\n" + body_text_string + "\n" + url_passed + "\n\n" + nyaa_comments_string)
    else:
        f = open(file_path + trunked_title + extra_title + ".txt", "x", encoding="utf-8")
        f.write(trunked_title + "\n\n" + body_text_string + "\n\n" + url_passed)
    f.close()
    print('SUCCESS! ' + trunked_title + " " + url_passed + ' DONE!')

    # flag handling
    # if there is "no list" flag and no "update" flag and it isn't on the list, add it to the list
    if not global_flags['--no-list'] and not global_flags['--update'] and not is_downloaded(str(url_passed)):
        print("Adding to downloaded.txt")
        downloaded_list_alias = open(download_txt_file_path, 'a+', encoding="utf-8")  # https://www.geeksforgeeks.org/python-append-to-a-file/
        downloaded_list_alias.write(title + ' ' + url_passed + '\n')
        downloaded_list_alias.close()
    # if "update" flag is on and it's not on the list, add it to the list
    elif global_flags['--update'] and not is_downloaded(str(url_passed)):
        print("Adding to downloaded.txt")
        downloaded_list_alias = open(download_txt_file_path, 'a+', encoding="utf-8") # https://www.geeksforgeeks.org/python-append-to-a-file/
        downloaded_list_alias.write(title + ' ' + url_passed + '\n')
        downloaded_list_alias.close()

    # check if the program is being used as an executable
    qBittorrent_check = True
    arguments_cleaned = [arg for arg in sys.argv[1:] if not arg.startswith('--')] # remove flags
    if len(arguments_cleaned) != 7: #gindfr
        qBittorrent_check = False
    else:
        for arg in arguments_cleaned:
            if not arg.isalnum() or '/' in arg or '\\' in arg: # check that the seven arguments are consistent with gindfr
                qBittorrent_check = True
            else:
                qBittorrent_check = False
                break

    if global_flags.get('--no-list') is False and global_flags.get('--write-new') is False and global_flags.get('--update') is False and qBittorrent_check is True:
        move_file_function(file_path, trunked_title + extra_title + ".txt")
    return None


def truncate_title(cleaned_title: str, file_title: str) -> str:
    cleaned_title = cleaned_title.strip()
    # my solution to the max windows path length problem while still maintaining readability of tit
    trunked_title, word = "", ""
    open_brackets = False
    i = 0
    if len(cleaned_title) * 2 + 38 <= 256:
        trunked_title = cleaned_title
    else:
        # Have cleaned_title reach same length as the file_title length
        while i < len(cleaned_title) and len(trunked_title) <= (256 - len(file_title) - 38):
            word += cleaned_title[i]

            # Add word to trunked_title. Word defined as ending in clos brackets or a space
            if cleaned_title[i] in '])】』' or cleaned_title[i] == ' ' and open_brackets is False:
                trunked_title += word
                word = ""
            elif cleaned_title[i] in '[(『':
                open_brackets = True
            i += 1

    trunked_title = re.sub(r'\s$|[,.\-_+]$', r'', trunked_title)
    return trunked_title


def load_js(url_passed: str) -> bs4.BeautifulSoup:
    driver.get(url_passed)
    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')


# i can longer follow it after adding the outer (third) loop because of *args
def remove_whitespace_in_tags(*html_things: bs4.element.Tag | bs4.element.NavigableString | bs4.ResultSet) -> None:
    for html_thing in html_things: # iterate through however many resultset arguments are passed
        # depth 0
        for element in html_thing: # resultset and bs4.element.tag are iterable, they contain either tag or navigablestring
            # and can be treated the same
            if isinstance(element, bs4.element.Tag): # nested tags can only be in tags
                if len(element.contents) > 1: # could be nested
                    for current_element in element.contents: # depth 1
                        if isinstance(current_element, bs4.element.NavigableString): # navigablestring seems to always be whitespace, extract
                            if current_element.isspace():
                                current_element.extract()
                        else: # it's a tag so could have nested tags, call itself
                            remove_whitespace_in_tags(current_element)
    return None


def find_content(url_passed: str, soup: bs4.BeautifulSoup) -> int:
    cleaned_title = ""
    body_text = ""
    title = ""
    col_num = 0

    if "nyaa" in url_passed and not "cache" in url_passed:
        soup = load_js(url_passed)
        for tag in soup.findAll("hr"):
            tag.decompose()
        for tag in soup.findAll("img"):
            if tag.get('title'):
                tag.append("{}".format(tag.get('title')))
            elif tag.get('alt'):
                tag.append("{}".format(tag.get('alt')))
            tag.append(" ({})".format(tag.get('src')))
            tag.smooth()
        # place above href to get the title before () in inserted after because the title is text in a <i> tag
        # nested in the <a> tag
        if soup.find("div", attrs={'class': 'torrent-file-list panel-body'}) is not None:
            file_title = next(soup.find("div", attrs={'class': 'torrent-file-list panel-body'}).stripped_strings)
        else:
            return -1
        for element in soup.findAll("a"):
            element.append(" ({})".format(element.get('href'))) # call get() method to get attributes
            element.smooth()

        for tag in soup.find("div", attrs={'id': 'torrent-description'}):
            # Rationale: if strong, probably contains code and em tags which are the tags most likely to feature broken up text
            # tag.<some_tag> checks if the child tag exists by tree traversal

            """# Two ways to avoid touching tables: check if a child tag is a tr tag or if the parent tag is a table tag
            The latter is harder to do since iterating is over the contents() collection, which omits the top-level tag ie. table)
            tag.tr same as (not tag.parent.name == 'table') same as (tag.parent.parent.table) since using point notation
            on an element means you have to be a level higher of the tag you want to refer to because I haven't
            figured out how to call the name of the tag on the level I am on"""

            # (thing inserted before)<tag><strong></string>[<...>, <...>, ....]</tag>
            if isinstance(tag, bs4.element.Tag) and (tag.strong or tag.code or tag.img or tag.a) and not tag.tr:
                p_tag = soup.new_tag("p")
                p_tag.string = tag.get_text()
                tag.insert_before(p_tag) # insert before the tag all the text unbroken as taken by
                # BeautifulSoup's get_text() method, but also put in as a tag so it isn't deleted later as navigablestring
                tag.decompose()
        remove_whitespace_in_tags(soup.find("div", attrs={'id': 'torrent-description'}))

        tables = soup.findAll("table")
        for table in tables:
            for i in range(len(table.findAll("tr"))):
                current_col_num = len(table.findAll("tr")[i].findAll("th"))
                if current_col_num > col_num:
                    col_num = current_col_num
        # an iterable with bs4.element.tag and bs4.NavigableString objects
        # remove annoying white space that soup parses as NavigableString
        for element in soup.find("div", attrs={'id': 'torrent-description'}):
            if isinstance(element, bs4.NavigableString):
                element.extract()
        # run it again now with fewer objects, running it in a separate loop is "safer" due to complications
        # resulting in removing elements as you are iterating over them in the loop above
        # loop to remove whitespace and empty lines
        for element in soup.find("div", attrs={'id': 'torrent-description'}):
            if not isinstance(element, bs4.element.NavigableString):  # still not sure why i have to extract
                if not (element.thead or element.tbody) and not str(element.string).strip() == '' and not element.img:
                    element.insert_before(re.sub(r'\s([?.!"](?:\s|$))', r'\1', element.get_text(separator="\n", strip=True)))
                    element.decompose()
        if soup.findAll("table"): # check if tables exist, if resultset is a list basically, a non-empty should
            # return true and an empty resultset should return false
            pd.set_option('display.max_colwidth', 0)
            df = pd.read_html(soup.prettify()) # make into html by calling prettify method
            # don't wrap tables that don't need it
            # find longest len of each table width-wise and use that as our pd width
            df_wrap = []
            for table in df:
                largest_df_width = 0
                for index in table.index:
                    curr_df_width = 0 # reset width counter for new row
                    for key in table:
                        # there's an issue where df fills empty with a float
                        if not isinstance(table.loc[index, key], float) and not isinstance(table.loc[index, key], numpy.int64) and not isinstance(table.loc[index, key], numpy.float64):
                            curr_df_width += len(table.loc[index, key])
                    if curr_df_width > largest_df_width:
                        largest_df_width = curr_df_width
                df_wrap.append(True) if largest_df_width + 14 > 175 else df_wrap.append(False)
            # edit tables in-place
            for table in df:
                for index in table.index:
                    for key in table:
                        if df_wrap[0]: # len(df_wrap) is same as len(df), so popping the first at end of each iteration of df is fine
                            table.loc[index, key] = textwrap.fill(str(table.loc[index, key]), int(175/col_num))
                        # remove df's read_html() fill of empty cells or None with nan and replace with empty string
                        if str(table.loc[index, key]) == 'nan':
                            table.loc[index, key] = ''
                df_wrap.pop(0)
            i = 0
            for element in soup.findAll("table"):
                element.insert_before(tabulate(df[i], headers='keys', tablefmt='grid'))
                if i < len(df):
                    i += 1
                element.decompose() # safe if the iterator is set at the for statement with pointers already set
                # from one element to the next in the iterable

        title_text = soup.find("div", {"class": "panel-heading"})
        for i in title_text.findAll("h3"):
            """translate() to avoid illegal windows filename
            ord() evaluates the unicode of each individual char in string and sees if it matches
            what's in the string that's in the loop
            a is our iterator that we use to iterate over a string, then pass the ord(a) of one iteration to translate
            where it looks for that char in that string then replaces that char with the char specified, returning
            it as a new string with the replacements"""
            cleaned_title = i.text.strip().translate({ord(a): None for a in '\/:*?"<>|'})
            title = i.text.strip()
        extra_text_initial1 = soup.findAll("div", {'class': 'col-md-1'}) # heading
        extra_text_initial2 = soup.findAll("div", {'class': 'col-md-5'}) # content
        # grabbed the second out of all the class=col-md-5 elements, which is the date
        # md-5: category, date, submitter, seeders, information, leechers, file size, completed
        filtered_content_indices = [1, 2, 6, 7] #date, submitter, file size, completed
        extra_text = bs4.element.Tag(None, None, 'p')

        remove_whitespace_in_tags(extra_text_initial2)

        for i in filtered_content_indices: # after clearing whitespace in tree, we can append
            # the same way we have in all the other site cases, add the soup-ish object to the
            # soup tree and output it all in one go in the write_function
            for a in extra_text_initial2[i]: # go through the elements we care about
                if isinstance(a, bs4.element.Tag): # if it's a tag, it has child tags
                    extra_text_initial2[i].insert(0, a.string) # insert the child tag string into the parent tag, decompose child
                    a.decompose()
            extra_text_initial2[i].insert(0, extra_text_initial1[i].string + " ") # put the heading strings into the content tags
            #extra_text.append(extra_text_initial1[i])
            extra_text.append(extra_text_initial2[i]) # append the complete string from the second bs4.element.Tag collection
        for a in extra_text: # append/insert requires smooth, otherwise contents() shows list
            a.smooth()
        # <p>a bunch of div tags for each of the things we filtered</p>
        for a in extra_text.findAll("div"): # iterate through div collection
            extra_text.append(a.string.extract()+"\n") # .string.extract() returns extracted string, add it to
            # extract the tag after the string
            a.extract()
        extra_text.smooth() # because we appended, it's in a list if we don't smooth()
        extra_text.string = extra_text.string[:-1] # remove last \n
        print(extra_text.string)
        extra_text.string = re.sub(r'^', r'\n', extra_text.string) # ^ match start of string
        body_text = soup.find("div", attrs={'id': 'torrent-description'})
        extra_text.append(body_text)
        body_text = extra_text
        remove_whitespace_in_tags(body_text)


    elif "cache" in url_passed and "nyaa" in url_passed:
        soup = load_js(url_passed)

        title_text = soup.find("h1", {"id": "entry_title"})
        cleaned_title = title_text.get_text().strip().translate({ord(a): None for a in '\/:*?"<>|'})
        file_title = cleaned_title
        title = title_text.text.strip()

        body_text += "Date: " + soup.find("time").get_text() + "\n"
        body_text += "Submitter: "
        for elm in soup.css.select('dd[class^="entry_submitter"]'):
            body_text += elm.get_text()
        body_text += "\n"
        body_text += "Size: " + soup.find("span", {"class": "number"}).get_text() + "\n"
        body_text += "Info hash: " + soup.find("dd", {"class": "entry_infohash"}).get_text() + "\n"
        body_text += "Description:" + "\n" + soup.find("div", {"id":"entry_description"}).get_text().strip() + "\n\n"

        body_text += "COMMENTS:\n"
        # comment per tr
        for i in range(0, len(soup.css.select('tr[id^="com"]'))):
            body_text += soup.css.select('tr[id^="com"]')[i].findAll("span")[0].get_text() + " — " # date
            body_text += soup.css.select('tr[id^="com"]')[i].findAll("span")[1].get_text() + "\n" # user
            body_text += soup.css.select('tr[id^="com"]')[i].findAll("div", {"class": "md_content"})[0].get_text() + "\n"

    # file_title is the actual title of the file/folder when you download the torrent
    # call stripped_strings() and next() after to strip the whitespace and iterate on the generator object
    # title will always be first element in the collection
    trunked_title = truncate_title(cleaned_title, file_title)
    write_function(trunked_title, body_text, url_passed, title, file_title, soup)
    return None


# print() and type() are very useful in debugging
def request_function(url_passed: str) -> None:
    open_sites = ['nyaa', 'cache']
    resp = ""
    open_sites_list = [True for keyword in open_sites if keyword in url_passed]
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


def is_downloaded(url: str) -> bool:
    downloaded_list_alias = open(download_txt_file_path, 'r', encoding="utf-8")
    text_content = downloaded_list_alias.readlines() # https://www.pythontutorial.net/python-basics/python-read-text-file/
    downloaded_list_alias.close()
    #if [True for a in text_content if url in a]:
    #if text_content.count(url) > 0: or if url_passed in text_content; neither work because any comparison
    # operation between string/bool to a list is always 0 or false
    for string in text_content:
        if url in string:
            return True
    return False


# --update: if on list, don't add to list, and write new text file; else add to list and write new text file
def main():
    flags = []
    for element in sys.argv[1:]:
        if element[0:2] == '--':
            flags.append(element[:].lower())
    # global flags are available flag options defined far above
    for global_flag in global_flags:
        for flag in flags:
            if global_flag == flag:
                global_flags[global_flag] = True
    # this needs a rework with new argument changes
    # for arg in sys.argv[1:len(sys.argv)-len(flags)]: # don't treat options as urls

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-CA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    for i in range(1,len(sys.argv)):
        if sys.argv[i][0:2] != '--': # process argument only if it is an infohash
            infohash = sys.argv[i]
            # 3 attempts at finding the nyaa url: 1) animetosho; 2) google search result page 1; 3) nyaa
            url = ""
            if not 'nyaa.si' in url:
                found_nyaa = False
                print("trying animetosho \n")
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
                        first_links = [link.get("href") for link in soup.find_all('a')]  # calling link['href'] errors if href is not defined in the tag
                        for link in first_links:
                            if link is not None and 'nyaa.si' in link:  # short circ eval in case of a value from get(key) returns none
                                found_nyaa = True
                                url = link
                                break
                        if found_nyaa:
                            check_nyaa_resp = requests.get(link)  # check if the original nyaa page is still up
                            if check_nyaa_resp.status_code == 404:  # not up, get cache page
                                print("404 nyaa.si page through animetosho")
                                first_links2 = [link.get("href") for link in soup.find_all('a')]
                                for i in range(0, len(first_links2)):
                                    if "cache" in first_links2[i]:
                                        url = first_links2[i]
                                        break
                        print(url)
                    else:
                        url = ""
            if not 'nyaa.si' in url and not 'cache' in url or requests.get(url, headers).status_code == 404:
                print("trying google search \n")
                url = "https://www.google.com/search?q={string}&sca_upv=1&uact=5".format(string=infohash)
                content = requests.get(url, headers=headers)
                soup = BeautifulSoup(content.text, "html.parser")
                page = soup.find(id='search')
                if page is not None:
                    first_links = [link['href'] for link in page.find_all('a')]
                    for link in first_links:
                        if 'nyaa.si' in link:
                            url = link
                            break
                else:
                    print("Google page is NoneType\n")
            if not 'nyaa.si' in url and not 'cache' in url or requests.get(url, headers).status_code == 404:
                print("trying nyaa search\n")
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
            if not url and not "https" in sys.argv[1]: # if url was not passed as arg 1
                print("URL not found\nEnding program or going next\n")
                # sys.exit(0)
            # flags
            if not is_downloaded(str(url)): # will execute (download) for flags --no-list or --update if it isn't already on list
                print("Requesting URL: " + str(url))
                request_function(str(url))
            elif global_flags['--update'] or global_flags['--no-list']: # ignore list
                request_function(str(url))
            else:
                print("Already downloaded, skipping: " + url)
    driver.close()
    driver.quit()
    sys.exit(1)
    return 0


if __name__ == '__main__':
    # if not "new prio" in sys.argv[1]:
    #      sys.exit(1)
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    # suppress annoying handshake failed ssl error msgs
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options)
    main()
