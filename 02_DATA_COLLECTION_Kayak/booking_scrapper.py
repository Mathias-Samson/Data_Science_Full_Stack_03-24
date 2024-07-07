import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
import json

class BookingcitySpider(scrapy.Spider):
    # Name Spider
    name = "BookingcitySpider"

    # Url to start
    start_urls = ['https://www.imdb.com/chart/boxoffice']

    # Function that will be called when starting your spider
    def parse(self,response):
      movies = response.xpath('/html/body/div[2]/main/div/div[3]/section/div/div[2]/div/ul/li')
      for movie in movies:
        yield {
            "ranking": movie.xpath('/div[2]/div/div/div/a/h3/text()').get().split(".")[0],
            "title": movie.xpath('/div[2]/div/div/div/a/h3/text()').get().split(".")[1].strip(" "),
            "url": movie.xpath('/div[2]/div/div/div/a').attrib["href"],
            "total_earnings": movie.xpath('/div[2]/div/div/ul/li[2]/span[2]/text()').get(),
            "rating": movie.xpath('/div[2]/div/div/span/div/span/text()').get(),
            "voters": movie.xpath('/div[2]/div/div/span/div/span/span/text()').getall()[1],
        }

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
filename = "imdb2.json"

if filename in os.listdir('/content/drive/MyDrive/Fichiers/2.Scolarité/1.Jedha_Data_Science/3.DATA_COLLECTION/M01_D09_WEB_SCRAPPING/src_Exo/résultat_exo/'):
        os.remove('/content/drive/MyDrive/Fichiers/2.Scolarité/1.Jedha_Data_Science/3.DATA_COLLECTION/M01_D09_WEB_SCRAPPING/src_Exo/résultat_exo/' + filename)

# Crowler Process

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/123.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        '/content/drive/MyDrive/Fichiers/2.Scolarité/1.Jedha_Data_Science/3.DATA_COLLECTION/M01_D09_WEB_SCRAPPING/src_Exo/résultat_exo/' + filename : {"format": "json"},
    }
})

process.crawl(imdb_spider)
process.start()