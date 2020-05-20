import scrapy

from items.tesco_items import ProductsItem


class TescoSpider(scrapy.Spider):
    name = 'tesco'
    allowed_domains = ['tesco.com']

    def start_requests(self):
        urls = ['https://www.tesco.com/groceries/en-GB/shop/', ]

        self.headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_departments, headers=self.headers, meta={"proxy": "http://quest.groupbwt.dev:9966"})

    def parse_departments(self, response):
        for link in response.xpath('//li[@class="list-item"]/a/@href').getall():
            print(link)
            if link.startswith("/groceries/en-GB/shop/"):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_departments, headers=self.headers, meta={"proxy": "http://quest.groupbwt.dev:9966"})

        for link in response.xpath('//div[@class="tile-content"]/a/@href').getall():
            print(link)
            if link.startswith('/groceries/en-GB/products/'):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_items, headers=self.headers, meta={"proxy": "http://quest.groupbwt.dev:9966"})

    def parse_items(self, response):
        product = ProductsItem()

        product_url = response.request.url
        product_id = product_url.split('/')[-1]
        product_image = response.xpath('//div[@class="product-image__container"]//img/@src').get()
        product_title = response.xpath('//div[@class="product-details-tile__title-wrapper"]/h1//text()').get()
        product_category = response.xpath('//div[@class="breadcrumbs__content"]//a/span//text()').get()
        product_price = response.xpath('//span[@data-auto="price-value"]//text()').get()

        reviews = []
        for review in response.xpath('//article[@class="review"]'):
            xpath_author = review.xpath('./p[@class="review-author"]/span[@class="review-author__nickname"]/text()') \
                .get()
            stars = review.xpath('./div/span[contains(text(), "stars")]/text()') \
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

        product['product_url'] = product_url
        product['product_id'] = product_id
        product['product_image'] = product_image
        product['product_title'] = product_title
        product['product_category'] = product_category
        product['product_price'] = product_price
        product['product_description'] = product_description
        product['reviews'] = reviews
        product['name_address'] = name_address
        product['return_address'] = return_address
        product['net_contents'] = net_contents
        product['recommended'] = recommended_products

        yield product
