import scrapy

from items.tesco_items import ProductsItem


class TescoSpider(scrapy.Spider):
    name = 'tesco'

    def start_requests(self):
        urls = [
            'https://www.tesco.com/groceries/en-GB/shop/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_departments)

    def parse_departments(self, response: scrapy.http.HtmlResponse):
        for link in response.xpath('//div[@class="tile-content"]/a/@href').getall():
            if link.startswith('/groceries/en-GB/products/'):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_items)

        for link in response.xpath('//li[@class="list-item"]/a/@href').getall():
            if link.startswith("/groceries/en-GB/shop/"):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_departments)

    def parse_items(self, response):
        more = response.xpath('//p[@class="reviews-list__show-more"]/a/@href').get()

        if more is not None:
            yield scrapy.Request(response.urljoin(more), callback=self.parse_items)

        products = ProductsItem()

        product_url = response.request.url
        product_id = product_url.split('/')[-1]
        product_image = response.xpath('//div[@class="product-image__container"]//img/@src').get()
        product_title = response.xpath('//div[@class="product-details-tile__title-wrapper"]/h1//text()').get()
        product_category = response.xpath('//div[@class="breadcrumbs__content"]//a/span//text()').get()
        product_price = response.xpath('//span[@data-auto="price-value"]//text()').get()

        reviews = []
        for review in response.xpath('//article[@class="review"]'):
            xpath_author = review.xpath('./p[@class="review-author"]/span[@class="review-author__nickname"]/text()')\
                                 .get()
            stars = review.xpath('./div/span[contains(text(), "stars")]/text()')\
                          .get().split(' ')
            reviews.append({
                'review_title': review.xpath('./h3[@class="review__summary"]/text()').get(),
                'stars': int(stars[0]) if len(stars) > 1 else "The information couldn't be fetched",
                'review_author': xpath_author if xpath_author else '',
                'review_date': review.xpath('./p[@class="review-author"]/span[@class="review-author__submission-time"]'
                                            '/text()').get(),
                'review_text': review.xpath('./p[@class="review__text"]/text()').get()
            })

        product_description = '\n'.join(response.xpath('//div[@id="product-description"]//text()').getall())
        name_address = '\n'.join(response.xpath('//div[@id="manufacturer-address"]//text()').getall())
        return_address = '\n'.join(response.xpath('//div[@id="return-address"]//text()').getall())
        net_contents = '\n'.join(response.xpath('//div[@id="net-contents"]//text()').getall())

        recommended_products = []
        for recommend in response.xpath('//div[@class="recommender-wrapper"]//div[@class="product-tile-wrapper"]'
                                        '//div[@class="tile-content"]'):
            recommended_products.append({
                'product_url': response.urljoin(recommend.xpath('./a/@href').get()),
                'product_title': recommend.xpath('./div[@class="product-details--wrapper-variant"]'
                                                 '/div/h3/a/text()').get(),
                'product_price': float(recommend.xpath('./div[@class="product-controls__wrapper"]'
                                                       '/form/div//span[@class="value"]/text()').get())
            })

        products['product_url'] = product_url
        products['product_id'] = product_id
        products['product_image'] = product_image
        products['product_title'] = product_title
        products['product_category'] = product_category
        products['product_price'] = product_price
        products['product_description'] = product_description
        products['reviews'] = reviews
        products['name_address'] = name_address
        products['return_address'] = return_address
        products['net_contents'] = net_contents
        products['recommended'] = recommended_products

        yield products