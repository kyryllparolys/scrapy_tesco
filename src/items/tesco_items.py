import scrapy


class ProductsItem(scrapy.Item):
    product_url = scrapy.Field()
    product_id = scrapy.Field()
    product_image = scrapy.Field()
    product_title = scrapy.Field()
    product_category = scrapy.Field()
    product_price = scrapy.Field()
    product_description = scrapy.Field()
    reviews = scrapy.Field()
    name_address = scrapy.Field()
    return_address = scrapy.Field()
    net_contents = scrapy.Field()
    recommended = scrapy.Field()