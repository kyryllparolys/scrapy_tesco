import scrapy
from lxml.html import fromstring


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
        product_image = response.xpath('//div[@class="product-image__container"]//img/@src').get()
        product_title = response.xpath('//div[@class="product-details-tile__title-wrapper"]/h1//text()').get()
        product_category = response.xpath(
            '//span[@class="beans-link__text styled__TextSpan-sc-1xizymv-3 hWdmzc"]//text()').get()
        product_price = response.xpath('//span[@data-auto="price-value"]//text()').get()

        reviews = []
        for review in response.xpath('//article[@class="review"]').getall():
            review = fromstring(review)
            review_author = review.xpath('//span[@class="review-author__nickname"]//text()')[0] if review.xpath(
                '//span[@class="review-author__nickname"]//text()') else ''

            reviews.append({
                'review_title': review.xpath('//h3//text()')[0],
                'stars': int(review.xpath('//span[contains(text(), "stars")]//text()')[0].split(' ')[0]),
                'review_author': review_author,
                'review_date': review.xpath('//span[@class="review-author__submission-time"]//text()')[0],
                'review_text': review.xpath('//p[@class="review__text"]//text()')[0]
            })

        product_description = '\n'.join(response.xpath('//div[@id="product-description"]//text()').getall())
        name_address = '\n'.join(response.xpath('//div[@id="manufacturer-address"]//text()').getall())
        return_address = '\n'.join(response.xpath('//div[@id="return-address"]//text()').getall())
        net_contents = '\n'.join(response.xpath('//div[@id="net-contents"]//text()').getall())

        recommended_products = []
        for recommend in response.xpath('//div[@class="recommender__wrapper"]//div[@class="product-tile-wrapper"]') \
                .getall():
            recommend = fromstring(recommend)
            recommended_products.append({
                'product_url': self.prefix_url + recommend.xpath('//a/@href')[0],
                'product_title': recommend.xpath('//a/text()')[0],
                'product_price': float(recommend.xpath('//div[@class="price-details--wrapper"]//text()')[2])
            })

        yield {
            'product_url': product_url,
            'product_id': int(product_id),
            'product_image': product_image,
            'product_title': product_title,
            'product_category': product_category,
            'product_price': float(product_price),
            'reviews': reviews,
            'product_description': product_description,
            'name_address': name_address,
            'return_address': return_address,
            'net_contents': net_contents,
            'recommended': recommended_products
        }
