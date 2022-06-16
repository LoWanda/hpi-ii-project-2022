# 1. get json
# iterate over entries
# 
companies = []
companies_file = open('../exports/corporate-entries2.json')
companies_string = companies_file.read()
companies_string = companies_string.split('\n')
for comp in companies_string:
    try: 
        company = json.loads(comp)
        companies.append(company["_source"])
    except:
        continue

# split entries based on local court

# iterate over partitions 
# look at reference id: split to pre part and number
# similarity measure based on these tokens compared to all following companies in the array
# WHICH ONE???? Levenshtein with swap? Fuzzywuzzy? 

# Threshold?? 

# if duplicate: create dedup entry => config 
# Use UPSERT, write.method=upsert, update schema


