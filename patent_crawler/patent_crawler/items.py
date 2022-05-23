# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PatentItem(scrapy.Item):
    patent_id = scrapy.Field()
    applicant = scrapy.Field()
    application_date = scrapy.Field()
    title = scrapy.Field()
    inventor = scrapy.Field()
    ipc_class = scrapy.Field()
    publication_date = scrapy.Field()
    legal_agents = scrapy.Field()
    
