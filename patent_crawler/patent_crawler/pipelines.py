# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from dpma_crawler.dpma_producer import DpmaProducer

from scrapy.utils.serialize import ScrapyJSONEncoder

class PatentPipeline:
    def __init__(self):
        self.producer = DpmaProducer()
        self.encoder = ScrapyJSONEncoder()

    def process_item(self, item, spider):
        msg = self.encoder.encode(item)
        self.producer.produce_to_topic(patent=msg)
