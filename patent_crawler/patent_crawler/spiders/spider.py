import scrapy
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

from dpma_crawler.constant import COOKIE
from build.gen.dpma.v2.patent_pb2 import Patent
from dpma_crawler.dpma_producer import DpmaProducer
from patent_crawler.items import PatentItem

from pydispatch import dispatcher

from scrapy import signals
import pandas as pd

from fuzzywuzzy import process, fuzz

class PatentSpider(scrapy.Spider):
    name = "patents"
    def __init__(self):
        self.num_requests = 0
        self.initial_date = datetime.today() - relativedelta(days=100)
        self.date = self.initial_date
        self.total = 0
        #self.producer = DpmaProducer()
        self.companies = []
        companies_file = open('../exports/corporate-entries2.json')
        companies_string = companies_file.read()
        companies_string = companies_string.split('\n')
        for comp in companies_string:
            try: 
                company = json.loads(comp)
                self.companies.append(company["_source"])
            except:
                continue
        self.company_names = [d['name'] for d in self.companies]
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
        print("Last Date =", self.date)

    def start_requests(self):
        while self.date > (self.initial_date - relativedelta(years=10)):
            url = f"https://register.dpma.de/DPMAregister/pat/experte?queryString=AT={self.date.day}.{self.date.month}.{self.date.year} and ST=anhaengig-in-kraft and SART=patent"
            self.date = self.date - timedelta(days=1)
            yield scrapy.Request(url=url, callback=self.parse, cookies=COOKIE, dont_filter=True)

    def parse(self, response):
        if ("Die Datenbankabfrage lieferte keine Treffer" in response.text) or ("Es sind folgende Fehler aufgetreten" in response.text) or  (": 0 Treffer" in response.text):
            yield
        elif "Trefferliste zu lang" in response.text:
            url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl:trefferlink"
            yield scrapy.Request(url=url, callback=self.get_patents, cookies=COOKIE, dont_filter=True)
        else:
            yield from self.get_patents(response)
        
    def get_patents(self, response):
        if ": 1 Treffer" in response.text: print("==========0")
        if "Registerauskunft\xa0Patent" in response.text:
            url = "https://register.dpma.de/DPMAregister/pat/trefferliste"
            yield scrapy.Request(url=url, callback=self.get_patents, cookies=COOKIE, dont_filter=True)
        else:
            for row in response.css("tr"):
                company = row.css("td[data-th*=Inhaber] *::text").get()
                if isinstance(company, type(None)):
                    continue
                
                if re.search("[0-9]{5}", company):
                    try: 
                        result = re.search("(.*), *([0-9]*) *(\S*),", company)
                        company_name = result.group(1)
                        company_plz = result.group(2)
                        company_town = result.group(3)
                    except:
                        continue
                else: 
                    try:
                        result = re.search("(.*), *(.*), *[A-Z]{2}$", company)
                        company_name = result.group(1)
                        company_plz = ""
                        company_town = result.group(2)
                    except:
                        continue

                best_company_match = process.extractOne(company_name, self.company_names, scorer=fuzz.ratio)

                if best_company_match[1] < 80:
                    continue
                else:
                    match = [x for x in self.companies if x["name"] == best_company_match[0] and ((company_plz == "" and company_town == "") or x["postal_code"] == company_plz or fuzz.ratio(x["city"], company_town) >= 80)]
                    if len(match) == 0:
                        continue
                    
                    match = match[0]
                    patent = Patent()
                    patent.id = row.css("td[data-th*=Aktenzeichen] a::text").get()
                    patent.applicant = company_name
                    patent.application_date = row.css("td[data-th*=Anmeldetag] *::text").get()
                    patent.title = row.css("td[data-th*=Bezeichnung] *::text").get()
                    patent.inventor.extend(row.css("td[data-th*=Erfinder] *::text").getall())
                    patent.ipc_class = row.css("td[data-th*=Hauptklasse] a::text").get()
                    patent.publication_date = row.css("td[data-th*=veröffentlichung] *::text").get()
                    patent.legal_agents.extend(row.css("td[data-th*=Vertreter] *::text").getall())
                    patent.company_reference =  match["reference_id"] + "_" + match["local_court"]
                    self.producer.produce_to_topic(patent=patent)

        if response.css("#blaetter_eins_vor::attr(disabled)").get() and response.css("#blaetter_eins_vor::attr(disabled)").get() != "disabled":
            yield scrapy.FormRequest.from_response(
                response,
                formid="form",
                clickdata={"name": "blaetter_eins_vor"},
                callback=self.get_patents,
                dont_filter=True,
                cookies=COOKIE)
