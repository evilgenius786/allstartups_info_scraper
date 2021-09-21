import csv
import os.path
import threading
import traceback

import requests
from bs4 import BeautifulSoup

site = 'https://www.allstartups.info'
headers = ['URL', 'Title', 'Website', 'Description', 'Stage', 'Platforms', 'Launched date', 'Published']
file = "allstartups.csv"
if not os.path.isfile(file):
    with open(file, 'w', newline='') as outfile:
        csv.writer(outfile).writerow(headers)
with open(file, 'r', encoding='utf8', errors='ignore') as o:
    outdata = o.read()

csvlock = threading.Lock()
txtlock = threading.Lock()


def scrape(links):
    rows = []
    global outdata
    for link in links:
        if link not in outdata:
            print(link)
            try:
                s = BeautifulSoup(requests.get(link).content, 'lxml')
                status = s.findAll('p', {'class': 'text-muted'})
                row = [link, s.find('h1').text.strip(), s.find('div', {'class': 'pull-left'}).text.strip()]
                try:
                    row.append(s.find('div', {'class': 'detail-body'}).text.strip().replace("\n", '').replace('\r', ''))
                except:
                    row.append("No Description")
                try:
                    row.append(status[0].text.strip())
                except:
                    row.append('No Stage')
                try:
                    row.append(s.find('ul', {'class': 'platforms'}).text.strip())
                except:
                    row.append('No platform')
                try:
                    row.append(status[1].text.strip())
                except:
                    row.append('No launched date')
                try:
                    row.append(status[2].text.strip())
                except:
                    row.append('No published date')
                print(row)
                rows.append(row)
                appendcsv(file, rows)
                outdata = outdata + link
            except Exception as e:
                print(f"URL Error: {link}", e)
                traceback.print_exc()
                appendtxt("error.txt", link)

        else:
            print(f"{link} already scraped")


def main():
    os.system('color 0a')
    logo()
    numthreads = 10
    for i in range(1, 600, numthreads):
        threads = []
        for j in range(i, i + numthreads):
            page = f"{site}/Startups?Page={j}"
            try:
                soup = BeautifulSoup(requests.get(page).content, 'lxml')
                print(f"Page: {page}")
                t = threading.Thread(target=scrape, args=(
                    [(site + x['href']) for x in soup.findAll('a', {'data-event-category': 'read-more'})],))
                threads.append(t)
                t.start()
            except Exception as e:
                traceback.print_exc()
                print(f"Page error : {page}", e)
                appendtxt("pages.txt", page)
        for thread in threads:
            thread.join()


def appendcsv(f, rows):
    csvlock.acquire()
    with open(f, 'a', newline='', encoding='utf8', errors='ignore') as outfile:
        csv.writer(outfile).writerows(rows)
    csvlock.release()


def appendtxt(f, line):
    txtlock.acquire()
    with open(f, 'a') as err:
        err.write(line + "\n")
    txtlock.release()


def logo():
    print("""
   _____  .__  .__      _________ __                 __                       .___        _____       
  /  _  \ |  | |  |    /   _____//  |______ ________/  |_ __ ________  ______ |   | _____/ ____\____  
 /  /_\  \|  | |  |    \_____  \\\\   __\__  \\\\_  __ \   __\  |  \____ \/  ___/ |   |/    \   __\/  _ \ 
/    |    \  |_|  |__  /        \|  |  / __ \|  | \/|  | |  |  /  |_> >___ \  |   |   |  \  | (  <_> )
\____|__  /____/____/ /_______  /|__| (____  /__|   |__| |____/|   __/____  > |___|___|  /__|  \____/ 
        \/                    \/           \/                  |__|       \/           \/             
=======================================================================================================
                 Scrapes all entries from AllStartups.info into CSV/XLSX
                        Developed by : fiverr.com/muhammadhassan7
=======================================================================================================
[+] Multithreaded
[+] Without browser
[+] Crash proof
[+] Resumable
[+] Without browser
""")


if __name__ == "__main__":
    main()
