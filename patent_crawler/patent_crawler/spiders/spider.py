import scrapy
import re

from dpma_crawler.constant import COOKIE
from build.gen.dpma.patent_pb2 import Patent
from dpma_crawler.dpma_producer import DpmaProducer
from patent_crawler.items import PatentItem

from pydispatch import dispatcher

from scrapy import signals


class PatentSpider(scrapy.Spider):
    name = "patents"
    def __init__(self):
        self.companies = ["Biontech", "Siemens"]
        self.num_requests = 0
        self.company = ""
        self.producer = DpmaProducer()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("Last Company: ", self.company)

    def start_requests(self):
        for company in self.companies:
            self.company = company
            url = f"https://register.dpma.de/DPMAregister/pat/experte?queryString=INH='{company}' and ST=anhaengig-in-kraft and SART=patent"
            yield scrapy.Request(url=url, callback=self.parse, cookies={"pat.checkedList": COOKIE}, dont_filter=True)

    def parse(self, response):
        if "Die Datenbankabfrage lieferte keine Treffer" in response.text:
            total_num = 0
        elif "Trefferliste zu lang" in response.text:
            # url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl.trefferanzahlexakt"
            # yield scrapy.Request(url=url, callback=self.get_total_num, cookies={"pat.checkedList": COOKIE}, dont_filter=True)
            url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl:trefferlink"
            yield scrapy.Request(url=url, callback=self.get_patents, cookies={"pat.checkedList": COOKIE}, dont_filter=True)
        else: 
            yield from self.get_patents(response)

    def get_total_num(self, response):
        total_num = response.css('span.gesamttre::text').extract_first()
        
        print(total_num)
        total_num = re.search(':( *)(.*)', total_num).group(2)
        
        
    def get_patents(self, response):
        for row in response.css("tr"):
            legal_agents = "".join(row.css("td[data-th*=Vertreter] *::text").getall())
            patent = Patent()
            if not row.css("td[data-th*=Anmelder] *::text").get():
                continue
            # patent["patent_id"] = row.css("td[data-th*=Aktenzeichen] a::text").get()
            # patent["applicant"] = "".join(row.css("td[data-th*=Inhaber] *::text").getall())
            # patent["application_date"] = row.css("td[data-th*=Anmeldetag] *::text").get()
            # patent["title"] = row.css("td[data-th*=Bezeichnung] *::text").get()
            # patent["inventor"] = row.css("td[data-th*=Erfinder] *::text").getall()
            # patent["ipc_class"] = row.css("td[data-th*=Hauptklasse] a::text").get()
            # patent["publication_date"] = row.css("td[data-th*=veröffentlichung] *::text").get()
            # patent["legal_agents"] = row.css("td[data-th*=Vertreter] *::text").getall()
            patent.id = row.css("td[data-th*=Aktenzeichen] a::text").get()
            patent.applicant = "".join(row.css("td[data-th*=Inhaber] *::text").getall())
            patent.application_date = row.css("td[data-th*=Anmeldetag] *::text").get()
            patent.title = row.css("td[data-th*=Bezeichnung] *::text").get()
            patent.inventor.extend(row.css("td[data-th*=Erfinder] *::text").getall())
            patent.ipc_class = row.css("td[data-th*=Hauptklasse] a::text").get()
            patent.publication_date = row.css("td[data-th*=veröffentlichung] *::text").get()
            patent.legal_agents.extend(row.css("td[data-th*=Vertreter] *::text").getall())
            # yield patent
            self.producer.produce_to_topic(patent=patent)

        if response.css("#blaetter_eins_vor::attr(disabled)").get() != "disabled":
            yield scrapy.FormRequest.from_response(
                response,
                formid="form",
                clickdata={"name": "blaetter_eins_vor"},
                callback=self.get_patents,
                dont_filter=True,
                cookies={"pat.checkedList": COOKIE})
