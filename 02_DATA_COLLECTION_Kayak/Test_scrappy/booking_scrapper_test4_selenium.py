import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BookinghotelSpider(scrapy.Spider):
    name = 'bookinghotel'
    allowed_domains = ['booking.com']
    start_urls = [
        'https://www.booking.com/searchresults.fr.html?ss=Paris&checkin=2024-07-10&checkout=2024-07-12&group_adults=2&no_rooms=1&group_children=0'
    ]

    def __init__(self, *args, **kwargs):
        super(BookinghotelSpider, self).__init__(*args, **kwargs)
        self.driver_service = Service(#find chromedriver for version 126.0.6478.114)
        #https://googlechromelabs.github.io/chrome-for-testing/
        self.driver = webdriver.Chrome(service=self.driver_service)

    def parse(self, response):
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="property-card"]'))
        )
        html_content = self.driver.page_source
        selenium_response = HtmlResponse(url=response.url, body=html_content, encoding='utf-8')

        property_cards = selenium_response.css('div[data-testid="property-card"]')
        
        for card in property_cards:
            if card.css('span:contains("Publicité")').get() is None:
                yield {
                    'name': card.css('div[data-testid="title"]::text').get(),
                    'url': card.css('a[data-testid="title-link"]::attr(href)').get(),
                    'score': card.css('div[data-testid="review-score"] span::text').get(),
                }

        next_page = selenium_response.css('a[title="Next page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def closed(self, reason):
        self.driver.quit()
