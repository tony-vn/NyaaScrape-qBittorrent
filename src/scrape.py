import textwrap
import bs4
import numpy
import pandas as pd
from tabulate import tabulate
import main
import sys
import re
import os
from os_utility import truncate_title
from os_utility import write_function
import global_variables as gv

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

def find_content(url_passed: str, soup: bs4.BeautifulSoup):
    cleaned_title = ""
    body_text = ""
    title = ""
    col_num = 0

    if gv.open_sites[0] in url_passed in url_passed:
        soup = main.load_js(url_passed)
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
        # (extra_text.string)
        extra_text.string = re.sub(r'^', r'\n', extra_text.string) # ^ match start of string
        body_text = soup.find("div", attrs={'id': 'torrent-description'})
        extra_text.append(body_text)
        body_text = extra_text
        remove_whitespace_in_tags(body_text)

        if gv.global_flags['--torrent-dir']:
            # print("In scrape, in condition where --torrent-dir cond. is true")
            # assumptions: all multifile torrents (series) are contained within a folder,  and all single files (movies) are not
            # if a multifile torrent does not have a folder, use the name of the first file as the folder name
            if soup.find("div", {'class': 'torrent-file-list panel-body'}).findAll("li")[0].find("a", {'class': 'folder'}):
                foldername = soup.find("div", {'class': 'torrent-file-list panel-body'}).findAll("li")[0].find("a", {'class': 'folder'}).get_text()
                # print("This is the foldername from folder", foldername)
                foldername = foldername[:-3] # strange " ()" appended
            else:
                filename = soup.find("div", {'class': 'torrent-file-list panel-body'}).findAll("li")[0].get_text()
                foldername = filename[:filename.rindex('(')-5] # 3 extension, 2 space and dot
                # print("This is the foldername from a single file", foldername)
            # assign the user specified path associated with the flag to the variable
            for i in range(0, len(sys.argv)):
                if sys.argv[i].lower() == '--torrent-dir' and os.path.isdir(sys.argv[i+1]):
                    gv.torrentdir_fullpath = sys.argv[i+1]
                    gv.torrentdir_fullpath = gv.torrentdir_fullpath + "\\{}".format(foldername)
                    gv.torrentdir_fullpath = gv.torrentdir_fullpath.replace(os.sep, '/')
                    # print("This is the torrentdir_fullpath in scrape", gv.torrentdir_fullpath)
                    break
    elif gv.open_sites[1] in url_passed:
        soup = main.load_js(url_passed)

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