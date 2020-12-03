import requests
import sys
import time
import threading
import math
import pandas as pd
import re
from collections import Counter
from bs4 import BeautifulSoup
from queue import Queue

all_articles = []
popular_articles = []
fit_article = []
picture = []
def crawl(start, end):
	for page_index in range(end+1, start+1):
		url = 'https://www.ptt.cc/bbs/Beauty/index' + str(page_index) + '.html'
		r2 = r.get(url)
		soup = BeautifulSoup(r2.text,'html.parser')
		title = soup.select('div.title')
		date = soup.select('div.date')
		pop = soup.select('div.nrec')
		for i, item in enumerate(title):
			if page_index < 2760:
				if str(date[i]).find('12/') >= 0:
					continue
			if page_index > 3135:
				if str(date[i]).find('1/') >= 0:
					continue
			if str(item).find('[公告]') >= 0:
				continue
			item_href = item.select_one('a').get('href')
			if len(str(item_href)) == 0:
				continue
			article_href = 'https://www.ptt.cc' + item_href
			# r3 = r.get(article_href)
			# soup = BeautifulSoup(r3.text,'html.parser')
			# results = soup.select('span.f2')
			# if str(results).find('※ 發信站') >= 0:
			rec = str(date[i]).split('>')[1].split('<')[0].replace('/', '').replace(' ', '') + ',' + item.text.replace('\n', '') + ',' + article_href
			if str(pop[i]).find('爆') >= 0:
				popular_articles.append(rec)
			all_articles.append(rec)
		time.sleep(0.1)

def push(start, end, q):
	up_count = 0
	down_count = 0
	up_id = Counter()
	down_id = Counter()
	for i in range(start, end):
		article_content = r.get(fit_article[i])
		soup = BeautifulSoup(article_content.text,'html.parser')
		if str(soup).find('※ 發信站') < 0:
			continue
		push = soup.select('div.push')
		for item in push:
			if len(str(item)) == 0:
				continue
			if str(item).find('warning-box') >= 0:
				continue
			push_tag = str(item).split('>')[2].split(' ')[0]
			user_id = str(item).split('>')[4].split('<')[0]

			if push_tag == '推': 
				up_id[user_id] += 1
				up_count += 1
			if push_tag == '噓':
				down_id[user_id] += 1
				down_count += 1
		time.sleep(0.1)
	answer = []
	answer.append(up_count)
	answer.append(down_count)
	answer.append(up_id)
	answer.append(down_id)
	q.put(answer)


def popular(start, end):
	for i in range(start, end):
		article_content = r.get(fit_article[i])
		soup = BeautifulSoup(article_content.text,'html.parser')
		if str(soup).find('※ 發信站') < 0:
			continue
		all_picture_url = re.findall(r'((https|http)://(.*)\.(jpg|png|jpeg|gif))' , str('\n'.join(soup.findAll(text=True))))
		for j in range(len(all_picture_url)):
			picture.append(all_picture_url[j][0])

def keyword_job(start, end, keyword):
	for i in range(start, end):
		article_content = r.get(fit_article[i])
		soup = BeautifulSoup(article_content.text,'html.parser')
		if str(soup).find('※ 發信站') < 0:
			continue
		target_content = '\n'.join(('\n'.join(soup.findAll(text=True))).split('返回看板')[1:]).split('※ 發信站')[0]
		if target_content.find('--\n') >= 0:
			target_content = target_content.rsplit('--\n', 1)[0]
		if str(target_content).find(keyword) >= 0:
			all_picture_url = re.findall(r'((https|http)://(.*)\.(jpg|png|jpeg|gif))' , str('\n'.join(soup.findAll(text=True))))
			for j in range(len(all_picture_url)):
				picture.append(all_picture_url[j][0])

if sys.argv[1] == 'crawl':
	require = []
	r = requests.Session()
	payload ={
	    'from':'/bbs/Beauty/index.html',
	    'yes':'yes'
	}
	url = 'https://www.ptt.cc/bbs/Beauty/index3143.html'
	r1 = r.post('https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex.html',payload)
	
	all_start = 3143
	all_end = 2740
	job_count = (all_start - all_end) / 6
	threads = []
	for i in range(6):
		start = 3143 - job_count * i
		end = 3143 - job_count * (i + 1)
		threads.append(threading.Thread(target = crawl, args = (int(start), int(end))))
		threads[i].start()
	for i in range(6):
  		threads[i].join()
		
	with open('./all_articles.txt', 'w') as f:
		for item in all_articles:
			f.write("%s\n" % item)
	with open('./all_popular.txt', 'w') as f:
		for item in popular_articles:
			f.write("%s\n" % item)

if sys.argv[1] == 'push':
	require = []
	r = requests.Session()
	payload ={
	    'from':'/bbs/Beauty/index.html',
	    'yes':'yes'
	}
	url = 'https://www.ptt.cc/bbs/Beauty/index3143.html'
	r1 = r.post('https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex.html',payload)

	df = pd.read_csv('./all_articles.txt', sep='\n', header = None)
	start_date = int(sys.argv[2])
	end_date = int(sys.argv[3])
	for i in range(len(df)):
		date = int(str(df[0][i]).split(',')[0])
		if date >= start_date and date <= end_date:
			url = str(df[0][i]).split(',')[-1]
			fit_article.append(url)
	job_count = int((len(fit_article)) / 6)
	threads = []
	q = Queue()
	for i in range(6):
		start = job_count * i
		end = job_count * (i + 1)
		if i == 5:
			end = len(fit_article)
		threads.append(threading.Thread(target = push, args = (start, end, q)))
		threads[i].start()
	total_up_count = 0
	total_down_count = 0
	total_up_id = Counter()
	total_down_id = Counter()
	for i in range(6):
		threads[i].join()
	for i in range(6):
		answer = q.get()
		total_up_count += answer[0]
		total_down_count += answer[1]
		total_up_id += answer[2]
		total_down_id += answer[3]
	total_up_id = sorted(total_up_id.items(), key= lambda t: (-t[1], t[0]))
	total_down_id = sorted(total_down_id.items(), key= lambda t: (-t[1], t[0]))
	with open('./push['+ str(start_date) + '-' + str(end_date) + '].txt', 'w') as f:
		f.write('all like: %d\n' % total_up_count)
		f.write('all boo: %d\n' % total_down_count)
		for i in range(0, 10, 1):
			f.write('like #%d: %s %d\n' % (i+1, total_up_id[i][0], total_up_id[i][1]))
		for i in range(1, 10, 1):
			f.write('boo #%d: %s %d\n' % (i+1, total_down_id[i][0], total_down_id[i][1]))
			
	

if sys.argv[1] == 'popular':
	require = []
	r = requests.Session()
	payload ={
	    'from':'/bbs/Beauty/index.html',
	    'yes':'yes'
	}
	url = 'https://www.ptt.cc/bbs/Beauty/index3143.html'
	r1 = r.post('https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex.html',payload)

	df = pd.read_csv('./all_popular.txt', sep='\n', header = None)
	start_date = int(sys.argv[2])
	end_date = int(sys.argv[3])
	for i in range(len(df)):
		date = int(str(df[0][i]).split(',')[0])
		if date >= start_date and date <= end_date:
			url = str(df[0][i]).split(',')[-1]
			fit_article.append(url)
	job_count = int((len(fit_article)) / 6)
	threads = []
	for i in range(6):
		start = job_count * i
		end = job_count * (i + 1)
		if i == 5:
			end = len(fit_article)
		threads.append(threading.Thread(target = popular, args = (start, end)))
		threads[i].start()
	for i in range(6):
		threads[i].join()

	with open('./popular[' + str(start_date) + '-' + str(end_date) + '].txt', 'w') as f:
		f.write('number of popular articles: %d\n' % len(fit_article))
		for item in picture:
			f.write("%s\n" % item)

if sys.argv[1] == 'keyword':
	keyword = str(sys.argv[2])
	start_date = int(sys.argv[3])
	end_date = int(sys.argv[4])
	require = []
	r = requests.Session()
	payload ={
	    'from':'/bbs/Beauty/index.html',
	    'yes':'yes'
	}
	url = 'https://www.ptt.cc/bbs/Beauty/index3143.html'
	r1 = r.post('https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex.html',payload)

	df = pd.read_csv('./all_articles.txt', sep='\n', header = None)
	for i in range(len(df)):
		date = int(str(df[0][i]).split(',')[0])
		if date >= start_date and date <= end_date:
			url = str(df[0][i]).split(',')[-1]
			fit_article.append(url)
	job_count = int((len(fit_article)) / 6)
	threads = []
	for i in range(6):
		start = job_count * i
		end = job_count * (i + 1)
		if i == 5:
			end = len(fit_article)
		threads.append(threading.Thread(target = keyword_job, args = (start, end, keyword)))
		threads[i].start()
	for i in range(6):
		threads[i].join()
	with open('./keyword(' + keyword + ')['+ str(start_date) + '-' + str(end_date) + '].txt', 'w') as f:
		for item in picture:
			f.write("%s\n" % item)
