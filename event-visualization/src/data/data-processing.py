import json
from collections import defaultdict


companies = []
companies_file = open('./corporate-entries_dedup.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
	try: 
		company = json.loads(comp)
		companies.append(company["_source"]) 
	except:
		continue

with open('companies.json', 'w', encoding='utf-8') as f:
    json.dump(companies, f, ensure_ascii=False, indent=4)