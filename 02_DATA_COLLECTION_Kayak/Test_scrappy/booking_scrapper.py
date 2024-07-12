import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin

class BookinghotelSpider(scrapy.Spider):
    name = "BookinghotelSpider"

    def __init__(self, cities=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cities_list = cities if cities else []
        self.cities_url = [
            f"https://www.booking.com/searchresults.fr.html?ss={city}&checkin=2024-07-10&checkout=2024-07-12&group_adults=2&no_rooms=1&group_children=0"
            for city in self.cities_list
        ]
        
    def start_requests(self):
        for url in self.cities_url:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        hotels = response.xpath("/html/body/div[4]/div/div[4]/div[1]/div[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div/div")

        for hotel in hotels:
            name = hotel.xpath("/html/body/div[4]/div/div[4]/div[1]/div[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div/div/h2").get().strip()
            score = hotel.xpath('/html/body/div[4]/div/div[4]/div[1]/div[1]/div[7]/div/div[3]/div/div[2]/div/button/div/div/div[1]/text()').get()
            description = hotel.xpath('/html/body/div[4]/div/div[4]/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/div[1]/div/div[2]/div/div/p[1]/text()').get()
            url_meta = response.xpath('/html/head/meta[44]/@content').get()
            url = urljoin(response.url, url_meta) if url_meta else None
            
            latitude_longitude_script = response.xpath('//script[contains(text(), "booking.env.b_map_center_latitude")]/text()').get()
            latitude = None
            longitude = None
            if latitude_longitude_script:
                # Extract latitude
                latitude_index = latitude_longitude_script.find('booking.env.b_map_center_latitude')
                if latitude_index != -1:
                    latitude_start_index = latitude_index + len('booking.env.b_map_center_latitude = ')
                    latitude_end_index = latitude_longitude_script.find(';', latitude_start_index)
                    latitude_str = latitude_longitude_script[latitude_start_index:latitude_end_index].strip()
                    latitude = float(latitude_str)

                # Extract longitude
                longitude_index = latitude_longitude_script.find('booking.env.b_map_center_longitude')
                if longitude_index != -1:
                    longitude_start_index = longitude_index + len('booking.env.b_map_center_longitude = ')
                    longitude_end_index = latitude_longitude_script.find(';', longitude_start_index)
                    longitude_str = latitude_longitude_script[longitude_start_index:longitude_end_index].strip()
                    longitude = float(longitude_str)

            yield {
                'hotel_name': name,
                'url': url,
                'score': score,
                'description': description,
                'latitude': latitude,
                'longitude': longitude,
            }

        # Handle pagination if necessary
        next_page = response.css('a.bui-pagination__link--next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

if __name__ == "__main__":
    cities_list = [
        "MontSaintMichel", "StMalo", "Bayeux", "LeHavre", "Rouen", "Paris", "Amiens", "Lille",
        "Strasbourg", "ChateauduHautKoenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon",
        "Annecy", "Grenoble", "Lyon", "GorgesduVerdon", "BormeslesMimosas", "Cassis", "Marseille",
        "AixenProvence", "Avignon", "Uzes", "Nimes", "AiguesMortes", "SaintesMariesdelamer",
        "Collioure", "Carcassonne", "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "LaRochelle"
    ]

    # If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
    file_path = r'G:\Mon Drive\Fichiers\2.Scolarité\1. Jedha_Data_Science\CERTIF_PROJECTS\ML_Engineer_Certification_Projects\02_DATA_COLLECTION_Kayak\booking_hotels.json'

    if filename in os.listdir(r'G:\Mon Drive\Fichiers\2.Scolarité\1. Jedha_Data_Science\CERTIF_PROJECTS\ML_Engineer_Certification_Projects\02_DATA_COLLECTION_Kayak'):
        os.remove(file_path)

    # Crawler Process
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Chrome/123.0',
        'LOG_LEVEL': logging.INFO,
        "FEEDS": {
            file_path: {"format": "json"},
        }
    })

    process.crawl(BookinghotelSpider, cities=cities_list)
    process.start()