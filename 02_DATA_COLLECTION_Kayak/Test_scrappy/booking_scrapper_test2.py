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
                "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "LaRochelle"
            ]
        self.cities_url = [
            f"https://www.booking.com/searchresults.fr.html?ss={city}&checkin=2024-07-10&checkout=2024-07-12&group_adults=2&no_rooms=1&group_children=0"
            for city in cities
        ]
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Opera";v="111", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        self.cookies = {
            'currency': 'USD',
            'language': 'en-gb',
        }
        self.log(f"Generated URLs: {self.cities_url}", level=logging.INFO)


    def start_requests(self):
        for url in self.cities_url:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        hotel_links = response.css('a.hotel_name_link::attr(href)').getall()
        for link in hotel_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_hotel)

    def parse_hotel(self, response):
        name = response.css('span.sr-hotel__name::text').get().strip()
        self.log(f'Processing hotel: {name}', level=logging.INFO)
        score = response.css('div.bui-review-score__badge::text').get()
        description = response.css('div.hotel_desc::text').get()
        coords = response.css('::attr(data-coords)').get()
        latitude, longitude = (coords.split(',') if coords else (None, None))

        yield {
            'hotel_name': name,
            'url': response.url,
            'score': score,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
        }

        next_page = response.css('a.bui-pagination__link--next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)


if __name__ == '__main__':
    file_path = r'G:\Mon Drive\Fichiers\2.Scolarité\1. Jedha_Data_Science\CERTIF_PROJECTS\ML_Engineer_Certification_Projects\02_DATA_COLLECTION_Kayak\booking_hotels.json'
    if os.path.exists(file_path):
        os.remove(file_path)

    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': logging.DEBUG,
        "FEEDS": {
            file_path: {"format": "json"},
        }
    })

    process.crawl(BookinghotelSpider, cities=cities_list)
    process.start()
