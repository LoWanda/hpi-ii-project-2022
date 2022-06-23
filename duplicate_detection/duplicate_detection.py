from collections import defaultdict
from fuzzywuzzy import fuzz

from build.gen.dedup.duplicate_pb2 import Duplicate
from rb_crawler.rb_producer_d import RbProducerD

producer = RbProducerD()

# 1. get json
# iterate over entries
# 

d = defaultdict(list)
companies = []
companies_file = open('../exports/corporate-entries2.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
		d[company["_source"]["local_court"]].append(company["_source"]) #dictionary splitted into local courts (blocking)
	except:
		continue

# iterate over partitions
threshold = 75
dedup_counter = 0
duplicates = dict()
for local_court, value in d.items():
	for index, company in enumerate(value):
		id = company["reference_id"]
		print(id)
		for next_company in value[i+1:]:
			next_id = next_company["reference_id"]
			# similarity measure based on tokens compared to all following companies in the array
			similarity = fuzz.token_sort_ratio(id, next_id)
			if similarity >= threshold:
				# transitivity
				if not duplicates[company["id"]] and not duplicates[next_company["id"]]:
					duplicates[company["id"]] = dedup_counter
					duplicates[next_company["id"]] = dedup_counter
					dedup_counter +=1
				if duplicates[company["id"]] and not duplicates[next_company["id"]]:
					duplicates[next_company["id"]] = duplicates[company["id"]]
				if not duplicates[company["id"]] and duplicates[next_company["id"]]:
					duplicates[company["id"]] = duplicates[next_company["id"]]
					

					
for id, dedup in duplicates.items():
	duplicate = Duplicate()
	duplicate.id = id
	duplicate.dedup_id = dedup
	producer.produce_to_topic(duplicate = duplicate)
		
print(duplicates)
print(d)
# look at reference id: split to pre part and number
# WHICH ONE???? Levenshtein with swap? Fuzzywuzzy? 

# if duplicate: create dedup entry => config 
# Use UPSERT, write.method=upsert, update schema


