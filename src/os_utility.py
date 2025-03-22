import glob
from main import *
import sys
import os
import shutil
import re

if sys.argv[0][-4:] == '.exe':
    exe_path = sys.executable  # Path to the actual .exe if frozen, otherwise Python interpreter
elif sys.argv[0][-3:] == '.py':
    exe_path = os.path.abspath(__file__)
exe_dir = os.path.dirname(exe_path)

# running qbittorrent as admin will create the folders and files at the installed qbittorrent folder i.e. c:\program files\qbittorrent
download_txt_file_path = exe_dir + "\\downloaded.txt"
download_txt_file_path = download_txt_file_path.replace(os.sep, '/')

readmes_folder_path = exe_dir + "\\readmes"
readmes_folder_path = readmes_folder_path.replace(os.sep, '/')

# make file if it does not exist
if not os.path.exists(readmes_folder_path):
    try:
        if len(readmes_folder_path) > 256 - len("\readmes"):
            raise Exception("Readmes path is too long. Path you've placed the executable or scripts in is too long. Try something less than 256.")
        os.makedirs(readmes_folder_path)
    except Exception as e:
        print(e)
if not os.path.exists(download_txt_file_path):
    try:
        if len(download_txt_file_path) > 256 - len("\downloaded.txt"):
            raise Exception("Downloaded.txt path is too long. Path you've placed the executable or scripts in is too long. Try something less than 256.")
        downloaded_list = open(download_txt_file_path, 'x', encoding="utf-8")
        downloaded_list.close()
    except Exception as e:
        print(e)
    
'''r for raw string; '\\'' interpreted as '\' however since '\' is the escape character in python, os.sep finds what
your os uses as separator for its path and replaces it with the char in the second argument'''

def is_downloaded(url: str) -> bool:
    downloaded_list_alias = open(download_txt_file_path, 'r', encoding="utf-8")
    text_content = downloaded_list_alias.readlines() # https://www.pythontutorial.net/python-basics/python-read-text-file/
    downloaded_list_alias.close()
    #if [True for a in text_content if url in a]:
    #if text_content.count(url) > 0: or if url_passed in text_content; neither work because any comparison
    # operation between string/bool to a list is always 0 or false
    for string in text_content:
        if url in string:
            print(f"This is the downloaded.txt file location (true): {download_txt_file_path} and its absolute path: {os.path.abspath(download_txt_file_path)}")
            print(f"this is the url that matched in the text file {url} and {string}")
            return True
    print(f"This is the downloaded.txt file location (true): {download_txt_file_path} and its absolute path: {os.path.abspath(download_txt_file_path)}")
    return False

def containsDuplicate(nums):
    """
    :type nums: List[int]
    :rtype: bool
    """
    aset = set()
    for num in nums:
        if num in aset:
            return True
        aset.add(num)
    return False

def move_file_function(readmes_folder_path: str, file_name: str) -> None:

    """
    the strings imported from qBittorrent are automatically imported into python with appropriate escaping of chars
    for the / eg. c:/folder is c://folder
    G I N D F R
    0 py or exe
    1 %G is tag/s (comma-separated)
    2 %I is the infohash
    3 %N is just the torrent name only, no path or anything else
    4 %D is the path holding the downloaded file
    5 %F is the path to the singular file (unsure for multipart torrent file)
    6 %R is the subfolder path created from selecting the option in qbittorrent

    DETERMINING THESE 3 CASES: 1) single file, no subfolder user choice; 2) single file, yes subfolder user choice; 3) is a folder
    Diff b/w 1) and 2) is the existence of file ext at arg3
        If arg6 empty, then 1): Create folder from arg3, put in arg4, move arg5 to arg4+new_folder
        If 2) and 3) Move file to arga6 if arg6 has no dupes, else move to arg4

    """
    arg_6 = sys.argv[6].split('\\')
    text_file_name = file_name.replace(os.sep, '/').split('/')[-1]
    destination_path = ""
    single_file_path = ""

    if sys.argv[6] == "": # is a "single file" w/ no subfolder so create one
        destination_path = sys.argv[5][:-sys.argv[5][::-1].index('.') - 1].replace(os.sep, '/') # backwards negative slice index minus one for before '.'
        single_file_path = sys.argv[5].replace(os.sep, '/') # folder name of folder to create

        # print('is a "single file" w/ no subfolder so create one')
        # print('media file path: '+ media_file_path)
        # print('destination_path: ' + destination_path)
        # print('text file path: ' + "{}/{}".format(readmes_folder_path, text_file_name))
        # print('destination_path: ' + destination_path)
    elif not containsDuplicate(arg_6): # is a "single file" with a created subfolder from qbittorrent
        destination_path = sys.argv[6].replace(os.sep, '/')
        # print('is a "single file" w/ subfolder')
        # print('text file path: ' + "{}/{}".format(readmes_folder_path, text_file_name))
        # print('destination_path: ' + destination_path)
    elif containsDuplicate(arg_6):
        destination_path = sys.argv[4].replace(os.sep, '/')
        # print('is folder')
        # print('text file path: ' + "{}/{}".format(readmes_folder_path, text_file_name))
        # print('destination_path: ' + destination_path)

    # validate destination path length
    try:
        if len(destination_path) > 256 - len(single_file_path):
            raise Exception("Destination path is too long. Try something less than 256.")
        if len(single_file_path) != 0:
            os.makedirs(destination_path)  # create new folder
            shutil.move(single_file_path, destination_path)  # move newly created folder
        shutil.move("{}/{}".format(readmes_folder_path, text_file_name), destination_path)  # move file
    except Exception as e:
        print(e)

    # destination_path = sys.argv[6].replace(os.sep, '/')
    # print("In move function, this is dest path 1 = " + destination_path)
    # # check file extension on the various qbittorrent arguments
    # if os.path.isdir(destination_path) and '.' in sys.argv[5] and 4 >= len(sys.argv[5][-sys.argv[5][::-1].index('.'):]) >= 3 or '.' in sys.argv[3] and 4 >= len(sys.argv[3][-sys.argv[3][::-1].index('.'):]) >= 3: # arg5 or 3 w/ file ext means single file
    #     file_name = file_name.replace(os.sep, '/').split('/')[-1]
    #     print("In a move condition true")
    #     shutil.move("{}/{}".format(file_path, file_name), "{}/{}".format(destination_path, file_name))
    #     print("Logging src path and destination path respectively: '{}' '{}'".format("{}/{}".format(file_path, file_name),"{}/{}".format(destination_path,file_name)))
    #     return None
    # elif '.' in sys.argv[3] and 4 >= len(sys.argv[3][-sys.argv[3][::-1].index('.'):]) >= 3:  # no subfolder case
    #     destination_path = sys.argv[4].replace(os.sep, '/')
    # elif '.' in sys.argv[5] and 4 >= len(sys.argv[5][-sys.argv[5][::-1].index('.'):]) >= 3:  # original content layout folder case
    #     destination_path = sys.argv[5].replace(os.sep, '/')
    # print("In move function, this is dest path 2 = " + destination_path)
    # shutil.move("{}/{}".format(file_path, file_name), "{}/{}".format(destination_path, file_name))
    # print("Logging src path and destination path respectively: '{}' '{}'".format("{}/{}".format(file_path, file_name),"{}/{}".format(destination_path,file_name)))
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
            pattern = re.sub(r'([\[\]])', r'[\1]', readmes_folder_path + trunked_title + extra_title) + "*.txt"
            result = glob.glob(pattern)
            new_version = len(result)
            old_name = readmes_folder_path + trunked_title + extra_title + ".txt"
            new_name = readmes_folder_path + trunked_title + extra_title + "v" + str(new_version) + ".txt"
        else:
            pattern = re.sub(r'([\[\]])', r'[\1]', (readmes_folder_path + trunked_title + extra_title)) + "*.txt"
            result = glob.glob(pattern)
            # the new version number is just the length of the list returned by glob
            new_version = len(result)
            # the old name is the current name
            old_name = readmes_folder_path + trunked_title + extra_title + ".txt"
            # the new name is the file name with v literal and the version number added
            # python quirk: if you add an int at the end, python expects ints for subsequent concats
            new_name = readmes_folder_path + trunked_title + extra_title + "v" + str(new_version) + ".txt"
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
        print(f"This is the readmes_folder_path: {readmes_folder_path}")
        print(f"This is the absolute readmes_folder_path: {os.path.abspath(readmes_folder_path)}")
        f = open(readmes_folder_path + '/' + trunked_title + extra_title + ".txt", "x", encoding="utf-8")
        f.write(title + "\n" + body_text_string + "\n" + url_passed + "\n\n" + nyaa_comments_string)
    else:
        print(f"This is the readmes_folder_path: {readmes_folder_path}")
        print(f"This is the absolute readmes_folder_path: {os.path.abspath(readmes_folder_path)}")
        f = open(readmes_folder_path + '/' + trunked_title + extra_title + ".txt", "x", encoding="utf-8")
        f.write(trunked_title + "\n\n" + body_text_string + "\n\n" + url_passed)
    # f.write("%G sys.argv[1] " + sys.argv[1] + "\n")
    # f.write("%I sys.argv[2] " + sys.argv[2] + "\n")
    # f.write("%N sys.argv[3] " + sys.argv[3] + "\n")
    # f.write("%D sys.argv[4] " + sys.argv[4] + "\n")
    # f.write("%F sys.argv[5] " + sys.argv[5] + "\n")
    # f.write("%R sys.argv[6] " + sys.argv[6] + "\n")
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

    if global_flags.get('--no-list') is False and global_flags.get('--write-new') is False and global_flags.get('--update') is False and is_executable():
        print("Calling move function")
        move_file_function(readmes_folder_path, trunked_title + extra_title + ".txt")
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

            # Add to trunked_title word-by-word. Word defined as ending in clos brackets or a space
            if cleaned_title[i] in '])】』' or cleaned_title[i] == ' ' and open_brackets is False:
                trunked_title += word
                word = ""
            elif cleaned_title[i] in '[(『':
                open_brackets = True
            i += 1

    trunked_title = re.sub(r'\s$|[,.\-_+]$', r'', trunked_title) # Remove invalid windows characters in filename
    return trunked_title