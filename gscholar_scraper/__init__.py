import scrapy.cmdline as cmdline
import time

while True:
    print "NEW RUN"
    cmdline.execute('scrapy crawl authorLabels -o popular_names.csv -t csv'.split(' '))

    print "executed "
    time.sleep(35)
