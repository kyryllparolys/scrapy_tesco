import scrapy

from items.tesco_items import ProductsItem


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
        for link in response.xpath('//div[@class="tile-content"]/a/@href').getall():
            if link.startswith('/groceries/en-GB/products/'):
                items_links.append(response.urljoin(link))

        if items_links:
            for link in items_links:
                yield scrapy.Request(link, callback=self.parse_items)

        for link in response.xpath('//li[@class="list-item"]/a/@href').getall():
            if link.startswith("/groceries/en-GB/shop/"):
                self.all_urls.append(response.urljoin(link))

        for link in self.all_urls:
            yield scrapy.Request(link, callback=self.parse_departments)

    def parse_items(self, response):
        products = ProductsItem()

        product_url = response.request.url
        product_id = product_url.split('/')[-1]
        product_image = response.xpath('//div[@class="product-image__container"]//img/@src').get()
        product_title = response.xpath('//div[@class="product-details-tile__title-wrapper"]/h1//text()').get()
        product_category = response.xpath('//div[@class="breadcrumbs__content"]//a/span//text()').get()
        product_price = response.xpath('//span[@data-auto="price-value"]//text()').get()

<<<<<<< HEAD
        # reviews = []
        # for review in response.xpath('//article[@class="review"]'):
        #     review_author = review.xpath('//span[@class="review-author__nickname"]//text()').get() if review.xpath(
        #         '//span[@class="review-author__nickname"]//text()').get() else ''
        #
        #     reviews.append({
        #         'review_title': review.xpath('//h3//text()').get(),
        #         'stars': int(review.xpath('//span[contains(text(), "stars")]//text()').get().split(' ')[0]),
        #         'review_author': review_author,
        #         'review_date': review.xpath('//span[@class="review-author__submission-time"]//text()').get(),
        #         'review_text': review.xpath('//p[@class="review__text"]//text()').get()
        #     })

=======
        reviews = []
        for review in response.xpath('//article[@class="review"]'):
            review_author = review.xpath('//span[@class="review-author__nickname"]//text()').get() if review.xpath(
                '//span[@class="review-author__nickname"]//text()').get() else ''

            reviews.append({
                'review_title': review.xpath('//h3[@class="review__summary"]//text()').get(),
                'stars': int(review.xpath('//span[contains(text(), "stars")]//text()').get().split(' ')[0]),
                'review_author': review_author,
                'review_date': review.xpath('//span[@class="review-author__submission-time"]//text()').get(),
                'review_text': review.xpath('//p[@class="review__text"]//text()').get()
            })
>>>>>>> b84054370202e8a82791c722f34c9cae7a63c3a2

        product_description = '\n'.join(response.xpath('//div[@id="product-description"]//text()').getall())
        name_address = '\n'.join(response.xpath('//div[@id="manufacturer-address"]//text()').getall())
        return_address = '\n'.join(response.xpath('//div[@id="return-address"]//text()').getall())
        net_contents = '\n'.join(response.xpath('//div[@id="net-contents"]//text()').getall())

        recommended_products = []
        for recommend in response.xpath('//div[@class="recommender__wrapper"]//div[@class="product-tile-wrapper"]'):
            recommended_products.append({
                'product_url': response.urljoin(recommend.xpath('//a/@href').get()),
                'product_title': recommend.xpath('//a/text()').get(),
                'product_price': float(recommend.xpath('//div[@class="price-details--wrapper"]//text()').getall()[2])
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