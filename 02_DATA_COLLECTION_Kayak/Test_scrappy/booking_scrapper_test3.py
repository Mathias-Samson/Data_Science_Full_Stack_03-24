import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin

class BookinghotelSpider(scrapy.Spider):
    name = "BookinghotelSpider"

    def __init__(self, cities=None, *args, **kwargs):
        super(BookinghotelSpider, self).__init__(*args, **kwargs)
        if cities is None:
            cities = [
                "MontSaintMichel", "StMalo", "Bayeux", "LeHavre", "Rouen", "Paris", "Amiens", "Lille",
                "Strasbourg", "ChateauduHautKoenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon",
                "Annecy", "Grenoble", "Lyon", "GorgesduVerdon", "BormeslesMimosas", "Cassis", "Marseille",
                "AixenProvence", "Avignon", "Uzes", "Nimes", "AiguesMortes", "SaintesMariesdelamer",
                "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne",
                "LaRochelle"
            ]
        self.cities_url = [
            f"https://www.booking.com/searchresults.fr.html?ss={city}&checkin=2024-07-10&checkout=2024-07-12&group_adults=2&no_rooms=1&group_children=0"
            for city in cities
        ]
        self.log(f"Generated URLs: {self.cities_url}", level=logging.INFO)

    def start_requests(self):
        for url in self.cities_url:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(f"Parsing URL: {response.url}", level=logging.INFO)

        hotel_links = response.css('div[data-testid="property-card"]').getall()

        for link in hotel_links:
            full_url = response.urljoin(link)
            self.log(f"Found link: {full_url}", level=logging.INFO)
            yield {'url': full_url}
        
        next_page = response.css('a.bui-pagination__link--next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

if __name__ == '__main__':
    file_path = r'G:\Mon Drive\Fichiers\2.Scolarité\1. Jedha_Data_Science\CERTIF_PROJECTS\Test scrappy\booking_hotels.json'
    if os.path.exists(file_path):
        os.remove(file_path)

    process = CrawlerProcess(settings={
        'USER_AGENT': 'Chrome/123.0',
        'LOG_LEVEL': logging.INFO,
        "FEEDS": {
            file_path: {"format": "json"},
        }
    })

    cities_list = [
        "MontSaintMichel", "StMalo", "Bayeux", "LeHavre", "Rouen", "Paris", "Amiens", "Lille",
        "Strasbourg", "ChateauduHautKoenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon",
        "Annecy", "Grenoble", "Lyon", "GorgesduVerdon", "BormeslesMimosas", "Cassis", "Marseille",
        "AixenProvence", "Avignon", "Uzes", "Nimes", "AiguesMortes", "SaintesMariesdelamer",
        "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne",
        "LaRochelle"
    ]

    process.crawl(BookinghotelSpider, cities=cities_list)
    process.start()
