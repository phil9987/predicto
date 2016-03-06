import requests
import re
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import string
from datetime import datetime,timedelta

#in Google Drive
#IMPORTHTML("url";"table";x)

def main():
    filename = 'urls.txt'
    #base_url = 'http://quotes.wsj.com/AAPL'
    #base_url = 'https://finance.yahoo.com/q/h?s=AAPL+Headlines'
    #base_url = 'https://finance.yahoo.com/q/h?s=AAPL&t=2016-03-04T09:00:00-05:00'
    pre_url = 'https://finance.yahoo.com/q/h?s=AAPL&t='
    post_url = 'T09:00:00-05:00'
    date = datetime.strptime("2016-02-29", "%Y-%m-%d")
    f = open(filename, 'a')
    urls = []
    for i in range(0,50):
        r = requests.get(pre_url + str(date.date()) + post_url)
        soup = BeautifulSoup(r.text,"html.parser")  # create 'soup' from reply text
        data = soup.findAll('div',attrs={'class':'mod yfi_quote_headline withsky'});
        for div in data:
            urls = [link.get('href') for link in div.findAll('a')]
        urls_ = []
        for url in urls[0:len(urls)-4]:
            split = string.split(url,'*')
            if len(split) > 1:
                urls_.append(split[1])
            else:
                urls_.append(url)
        for url in urls_:
            print url
        for url in urls_:
            s1 = '[' + "'%s'" % str(date.date()) + ',' + "'%s'" %str(url) + '],'
            f.write(s1)
            urls.append(s1)
        date = date -timedelta(minutes=59, hours=23, seconds=59)
    f.close()
    return 0

if __name__ == "__main__":
    main()