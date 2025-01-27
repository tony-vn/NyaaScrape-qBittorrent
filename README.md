# NyaaScrape-qBittorrent
********************************

### Description:
A simple script packaged into an executable that scrapes the download page of the site, writes the information from the page to a text file, and saves that text file at the location of the download. It attempt to scrape the nyaa page, and if that is unavailable, it will then try to scrape the cached nyaa page through animetosho.
<BR><BR>
Useful for providing a quick way to refer back to the torrent for details if the author included any, if the torrent is ever taken down, or if you want to know the particular date of the release in case you want to update to something newer.
<BR><BR>
What information does this executable scrape?
- Title
- Date
- Submitter
- File Size
- Number of Completes
- Description
- URL of the page
- All comments
<BR><BR>

### Usage Notes:
A record of pages scraped is kept in a file located in the same directory as the executable called "downloads.txt". This acts as a record of torrents you've downloaded. If you want to scrape the same page again, you will have to manually find the record from this text file and delete its entry. This is quite trivial albeit a little tedious to do, but it is as simple as finding the record (kept per line) and deleting it.

### Prerequisites:
For non-Windows users, the following Python modules are required: bs4, requests, sys, os, pandas, tabulate, selenium, re, textwrap, shutil and glob.
<BR><BR>
Note: the filenames of the generated text files are Windows filename compliant, but were not checked to be compliant for macOS and Linux filename systems. Whether this program works for these OSes is unclear.

### Setup:
In the settings of qBittorrent: Options -> Downloads -> Run external program -> Run on torrent finished
<BR><BR>
Check "Run on torrent finished", then add the line: "path/to/executable/NyaaScrape-qBittorrent.exe" "%G" "%I" "%N" "%D" "%F" "%R"

### Additional Information:
Users who want to scrape nyaa.si pages without qBittorrent can still do so by using the python file (from src folder) as a script. They must provide as arguments infohashes of the torrent when calling the script (multiple infohashes supported) for the torrent pages they want to scrape from.
<BR><BR>
The files will be saved in a folder located in the same directory as the script called readmes.
<BR><BR>
Additionally, several flags are available:
- `--no-list`: scrapes the web page, ignoring downloaded.txt, but will do nothing if the file already exists in the readmes directory
- `--write-new`: scrapes the web page but only if it is not recorded in the downloaded.txt, records it in downloaded.txt, and if another copy exists in readmes, it will rename
- `--update`: scrapes web page, add to downloaded.txt, and renames file if another copy exists in readmes (probably what you want to use in most cases).
<BR><BR>
*No order on flags or URLs
<BR><BR>

#### Examples:
##### General:
`python NyaaScrape-qBittorrent.py <flags> <infohash_here>`
##### Specific:
`python NyaaScrape-qBittorrent.py --update 5812b0b5b57f4c4bc814e4ad40a628dd9176d533`

### Update Considerations:
- Add proper table parsing for cached pages from animetosho like it exists for nyaa pages
- Refactor code
- Add intuitive (less technical) customizability for end-users (e.g. allow users a way to specify scraping the same page twice without needing to delete the entry in the downloads.txt)
- Provide non-Windows OSes support
- Fix possible logical errors regarding flags
- Add robustness to code






