import requests
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

def make_indeed_url(search_job, search_location):
    job = search_job.replace(' ', '%20')
    location = search_location.replace(',', '%2C').replace(' ', '%20')
    indeed_job_url = f'https://www.indeed.com/jobs?q={job}&l={location}'
    return indeed_job_url

def get_data(url, header):
    session = requests.session()
    scraper = cloudscraper.create_scraper(browser='chrome', sess=session)
    page = scraper.get(url,headers=header)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def find_url(soup):
    href_list = []
    base_link="https://in.indeed.com"
    divs = soup.find_all('div', class_ = 'job_seen_beacon')
    for j in divs:
        for i in j.find_all('a'):
            if i.has_attr( "href" ):
                k=i['href']
                href_list.append(base_link+k)
    return href_list

def transform(soup):
    joblist = []
    divs = soup.find_all('div', class_ = 'job_seen_beacon')
    href_list=find_url(soup)
    counter = 0
    for item in divs:
        title = item.find('a').text.strip()
        company = item.find('span', class_ = 'companyName').text.strip()
        try:
            salary = item.find('span', class_ = 'estimated-salary').text.strip()
        except:
            salary = 'No salary'
        summary = item.find('div', {'class':'job-snippet'}).text.strip()
        release_date = item.find('span', class_ = 'date').text.strip()
        counter+=1
        jobs = {
            'title': title,
            'link': href_list[counter],
            'company': company,
            'salary': salary,
            'date': release_date,
            'summary': summary
        }
        joblist.append(jobs)
    return joblist 
    
def main():
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    print("Enter job title: ")
    job_title = input()
    print("Enter job location: ")
    job_location = input()
    print("Numbers of pages to search: ")
    page = input()
    page_num = int(page) * 10
    for i in range(0,page_num,10):
        url = make_indeed_url(job_title, job_location) + '&start=' + str(i)
        c = get_data(url, header)
        job_info = transform(c)
        df = pd.DataFrame(job_info)
        if i == 0:
            df.to_csv('jobs.csv', mode='w', index = False)
        else:
            df.to_csv('jobs.csv', mode='a', index=False, header=False)

    data = pd.read_csv('jobs.csv')
    print(data)
    

if __name__ == '__main__':
    main()
