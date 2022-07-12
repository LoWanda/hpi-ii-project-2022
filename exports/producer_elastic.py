from build.gen.bakdata.announcement.announcement_pb2 import Announcement
from rb_crawler.rb_producer_a import RbProducerA

from build.gen.bakdata.corporate.v2.corporate_pb2 import Corporate
from rb_crawler.rb_producer_c import RbProducerC

from build.gen.dedup.duplicate_pb2 import Duplicate
from rb_crawler.rb_producer_d import RbProducerD

from build.gen.dpma.v2.patent_pb2 import Patent
from dpma_crawler.dpma_producer import DpmaProducer

import json


self.producer_c = RbProducerC()
self.producer_a = RbProducerA()
self.producer_d = RbProducerD()
self.producer_p = DpmaProducer()

companies = []
companies_file = open('./corporate-entries_dedup.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
        producer.produce_to_topic(corporate=company["_source"])
	except:
		continue

companies = []
companies_file = open('./announcements2.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
        producer.produce_to_topic(announcement=company["_source"])
	except:
		continue

companies = []
companies_file = open('./duplicates.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
        producer.produce_to_topic(duplicate=company["_source"])
	except:
		continue

companies = []
companies_file = open('./patent-events.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
        producer.produce_to_topic(patent=company["_source"])
	except:
		continue