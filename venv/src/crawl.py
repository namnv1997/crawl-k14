import json
import codecs
import requests
import bs4
import boto3
import arrow
from datetime import date, timedelta, datetime
import output

base_url = "http://kenh14.vn/"

def crawl_data_by_categories(list_categories):
    for category in list_categories:
        sub_link = "http://kenh14.vn/" + category + "/{}.chn"
        start_day = date(2019, 7, 1)
        end_day = date(2019, 7, 2)
        count_day = 1
        numbers_day = end_day - start_day
        while end_day != start_day:
            day = int(end_day.day)
            month = end_day.month
            year = end_day.year
            end_day -= timedelta(days=1)
            day_crawl = str(day)+"-"+str(month)+"-"+str(year)
            print(category.upper() + " PART " + str(count_day) + "/" + str(numbers_day.days))
            get_links_by_day(sub_link.format(day_crawl), category)
            count_day += 1


def get_links_by_day(link_day, category_name):
    req = requests.get(link_day)
    print(link_day)
    if req.ok:
        src = bs4.BeautifulSoup(req.content, 'lxml')
        links = src.select('h3.knswli-title > a')
        count = 0
        result = ""
        for a in links:
            article = get_article_content(base_url + a.attrs['href'][1:])
            # f = open('../output/'+category_name+'.txt', encoding='utf8', mode='a+')
            # f.write(str(article['content']))
            # f.write('\n')
            count += 1
            result += article['content'] + "\n"
            print(str(round(count*100/len(links), 2)) + "%")
    else:
        print('Not Success')
    update_object_s3(category_name, 'sia-03-project-data-source-2', result)

def get_article_content(url):
    data = {}
    req = requests.get(url)
    if req.ok:
        src = bs4.BeautifulSoup(req.content, 'lxml')
        #
        # title = src.select_one('h1.kbwc-title')
        # data['title'] = title.text.strip() if title else ''
        #
        # head_title = src.select_one('h2.knc-sapo')
        # data['head_title'] = head_title.text.strip() if head_title else ''

        content = src.select_one('.knc-content')
        data['content'] = content.text.strip() if content else ''
        #
        # pub_date = src.select_one('span.kbwcm-time')
        # data['pub_date'] = pub_date.text.strip() if pub_date else ''
    return data

def update_object_s3(category_name, bucketName, content):
    s3 = boto3.client('s3')
    time_up = datetime.today().strftime("%m-%d-%Y")
    file_name_aws = "kenh14/" + time_up + '/' + category_name + '.txt'
    try:
        # response = s3.put_object(file_name_computer, bucketName, file_name_aws)
        s3.put_object(Body=content, Bucket=bucketName, Key=file_name_aws)
    except Exception:
        return None
list_categories = ['star', 'tv-show', 'cine', 'musik', 'beauty-fashion', 'doi-song', 'an-ca-the-gioi', 'xa-hoi', 'the-gioi', 'sport', 'hoc-duong']
crawl_data_by_categories(list_categories)

