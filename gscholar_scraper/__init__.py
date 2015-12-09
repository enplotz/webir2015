import scrapy.cmdline as cmdline
import time


cmdline.execute('scrapy crawl authorLabels -s JOBDIR=crawls/author_labels -o popular_names.csv -t csv'.split(' '))

