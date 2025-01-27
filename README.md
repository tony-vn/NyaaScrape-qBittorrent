# NyaaScrape-qBittorrent
********************************

### Description:
A simple script packaged into an executable that scrapes the download page of the site, writes the information from the page to a text file, and saves that text file at the location of the download. 
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
A record of pages scraped is kept in a file located in the same directory as the executable called "downloads.txt". This acts as a record of torrents you've downloaded. If you want to scrape the same page again, you will have to manually find the record from this text file and delete its entry. This is quite trivial albeit a little tedious sometimes to do, but it is as simple as finding the record (kept per line) and deleting it.

### Prerequisites:
For non-Windows users, the following Python modules are required: bs4, requests, sys, os, pandas, tabulate, selenium, re, textwrap, shutil and glob.

### Setup:
In the settings of qBittorrent: Options -> Downloads -> Run external program -> Run on torrent finished <BR> <BR>
Check "Run on torrent finished", then add the line: "path/to/executable/NyaaScrape-qBittorrent.exe" "%G" "%I" "%N" "%D" "%F" "%R"

### Update Plans:
- Properly parse tables for cached pages from animetosho.org
- Refactor code
- Add intuitive (less technical) customizability for end-users (e.g. allow users a way to specify scraping the same page twice without needing to delete the entry in the downloads.txt)

### Additional Information:
