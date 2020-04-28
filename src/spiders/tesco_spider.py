import scrapy


class TescoSpider(scrapy.Spider):
    name = 'tesco'

    def start_requests(self):
        urls = [
            'https://www.tesco.com/groceries/en-GB/shop/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        