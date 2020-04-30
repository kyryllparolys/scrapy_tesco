import scrapy


class TescoSpider(scrapy.Spider):
    name = 'tesco'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.prefix_url = "https://www.tesco.com"
        self.all_urls = []

    def start_requests(self):
        urls = [
            'https://www.tesco.com/groceries/en-GB/shop/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_departments)

    def parse_departments(self, response: scrapy.http.HtmlResponse):
        items_links = []
        for link in response.xpath('//div[@class="tile-content"]').css('a').xpath('@href').getall():
            if link.startswith('/groceries/en-GB/products/'):
                items_links.append(self.prefix_url + link)

        if items_links:
            for link in items_links:
                yield scrapy.Request(link, callback=self.parse_items)

        for link in response.xpath('//li[@class="list-item"]').css('a').xpath('@href').getall():
            if link.startswith("/groceries/en-GB/shop/"):
                self.all_urls.append(self.prefix_url + link)

        for link in self.all_urls:
            yield scrapy.Request(link, callback=self.parse_departments)

    def parse_items(self, response: scrapy.http.Response):
        product_url = response.request.url
        product_id = product_url.split('/')[-1]
        product_image = response.xpath('//div[@class="product-image__container"]//img/@src').extract()
        product_title = response.xpath('//div[@class="product-details-tile__title-wrapper"]/h1//text()').get()
        category = response.xpath(
            '//span[@class="beans-link__text styled__TextSpan-sc-1xizymv-3 hWdmzc"]//text()').get()
        price = response.xpath('//span[@data-auto="price-value"]//text()').get()

        yield {
            'product_url': product_url,
            'product_id': product_id,
            'product_image': product_image,
            'product_title': product_title,
            'category': category,
            'price': price,
        }