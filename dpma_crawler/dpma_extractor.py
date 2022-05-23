import logging
from time import sleep

import json

import re 
import requests
from parsel import Selector

from build.gen.dpma.patent_pb2 import Patent
from dpma_producer import DpmaProducer
from dpma_crawler.constant import COOKIE

log = logging.getLogger(__name__)

class DpmaExtractor:
    def __init__(self):
        self.companies = ["Biontech"]
        # self.producer = DpmaProducer()

    def extract(self):
        for company in self.companies:
            session = requests.Session()
            session.cookies.set("pat.checkedList", COOKIE)
            log.info(f"Sending Request for: {company}")
            response = self.send_request(company, session)
            if "Die Datenbankabfrage lieferte keine Treffer" in response:
                print("Keine Treffer")
                exit(0)
            elif "Trefferliste zu lang" in response:
                response = session.get(url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl.trefferanzahlexakt").text
                selector = Selector(text=response)
                num = selector.css('span.gesamttre::text').extract_first()
                num = re.search(':( *)(.*)', num).group(2)
                response = session.get(url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl:trefferlink").text
            selector = Selector(text=response)
            for row in selector.css("tr"):
                patent = Patent()
                if not row.css("td[data-th*=Anmelder] *::text").get():
                    continue
                patent.id = row.css("td[data-th*=Aktenzeichen] a::text").get()
                patent.applicant = "".join(row.css("td[data-th*=Inhaber] *::text").getall())
                patent.application_date = row.css("td[data-th*=Anmeldetag] *::text").get()
                patent.title = row.css("td[data-th*=Bezeichnung] *::text").get()
                patent.inventor.extend(row.css("td[data-th*=Erfinder] *::text").getall())
                patent.ipc_class = row.css("td[data-th*=Hauptklasse] a::text").get()
                patent.publication_date = row.css("td[data-th*=veröffentlichung] *::text").get()
                patent.legal_agents.extend(row.css("td[data-th*=Vertreter] *::text").getall())

            if selector.css("#blaetter_eins_vor::attr(disabled)").get() != "disabled":
                # request_dict = {'Data': {'t:submit': "[\"blaetter_eins_vor\",\"blaetter_eins_vor\"]"}}
	
                # data = {   # open in bytes-mode
                #     'Request': json.dumps(request_dict)     # formats the dict to json text
                # }
                #url="https://register.dpma.de/DPMAregister/pat/experte.trefferauswahl"
                form_data = selector.css("input[name*='t:formdata']::attr(value)").get()
                res_link = selector.css("input[name*='researchLink']::attr(value)").get()
                page = selector.css("input[name*='aktuelleInputSeitenZahl']::attr(value)").get()
                data = {"t:submit":["blaetter_eins_vor","blaetter_eins_vor"],
                "t:formdata":form_data,
                "researchLink":res_link,
                "tConfigEingeklappt":"true",
                "checkbox_1":"on",
                "checkbox_2":"on",
                "checkbox_3":"on",
                "checkbox_4":"on",
                "checkbox_5":"on",
                "checkbox_6":"on",
                "checkbox_7":"on",
                "checkbox_8":"on",
                "checkbox_9":"on",
                "checkbox_10":"on",
                "sortierSpalte":"Aktenzeichen",
                "select_0":"aufsteigend",
                "trefferProSeite":"100",
                "aktuelleInputSeitenZahl":page,
                "blaetter_eins_vor":">",
                "anzGesamtAuswahl": "",
                "cookieDummy": ""}
                url="https://register.dpma.de/DPMAregister/pat/trefferliste.kopf.form"
                response = session.post(url, data=data).text
                
                selector = Selector(text=response)
                print(response)
            for row in selector.css("tr"):
                patent = Patent()
                if not row.css("td[data-th*=Anmelder] *::text").get():
                    continue

                patent.applicant = "".join(row.css("td[data-th*=Inhaber] *::text").getall())
                patent.application_date = row.css("td[data-th*=Anmeldetag] *::text").get()
                patent.title = row.css("td[data-th*=Bezeichnung] *::text").get()
                patent.inventor = "\n".join(row.css("td[data-th*=Erfinder] *::text").getall())
                patent.ipc_class = row.css("td[data-th*=Hauptklasse] a::text").get()
                patent.publication_date = row.css("td[data-th*=veröffentlichung] *::text").get()
                patent.legal_agents = "\n".join(row.css("td[data-th*=Vertreter] *::text").getall())
            print(patent)
                
            # Seiten durchgehen

        # while True:
        #     try:
                
        #         if "Falsche Parameter" in text:
        #             log.info("The end has reached")
        #             break
        #         selector = Selector(text=text)
        #         corporate = Corporate()
        #         corporate.rb_id = self.rb_id
        #         corporate.state = self.state
        #         corporate.reference_id = self.extract_company_reference_number(selector)
        #         event_type = selector.xpath("/html/body/font/table/tr[3]/td/text()").get()
        #         corporate.event_date = selector.xpath("/html/body/font/table/tr[4]/td/text()").get()
        #         corporate.id = f"{self.state}_{self.rb_id}"
        #         raw_text: str = selector.xpath("/html/body/font/table/tr[6]/td/text()").get()
        #         self.handle_events(corporate, event_type, raw_text)
        #         self.rb_id = self.rb_id + 1
        #         log.debug(corporate)
        #     except Exception as ex:
        #         log.error(f"Skipping {self.rb_id} in state {self.state}")
        #         log.error(f"Cause: {ex}")
        #         self.rb_id = self.rb_id + 1
        #         continue
        exit(0)

    def send_request(self, company:str, session) -> str:
        url = f"https://register.dpma.de/DPMAregister/pat/experte?queryString=INH='{company}' and ST=anhaengig-in-kraft and SART=patent"
        #url = f"https://www.handelsregisterbekanntmachungen.de/skripte/hrb.php?rb_id={self.rb_id}&land_abk={self.state}"
        # For graceful crawling! Remove this at your own risk!
        sleep(0.5)
        return session.get(url=url).text

    # @staticmethod
    # def extract_company_reference_number(selector: Selector) -> str:
    #     return ((selector.xpath("/html/body/font/table/tr[1]/td/nobr/u/text()").get()).split(": ")[1]).strip()

    # def handle_events(self, corporate, event_type, raw_text):
    #     if event_type == "Neueintragungen":
    #         self.handle_new_entries(corporate, raw_text)
    #     elif event_type == "Veränderungen":
    #         self.handle_changes(corporate, raw_text)
    #     elif event_type == "Löschungen":
    #         self.handle_deletes(corporate)

    # def handle_new_entries(self, corporate: Corporate, raw_text: str) -> Corporate:
    #     log.debug(f"New company found: {corporate.id}")
    #     corporate.event_type = "create"
    #     corporate.information = raw_text
    #     corporate.status = Status.STATUS_ACTIVE
    #     self.producer.produce_to_topic(corporate=corporate)

    # def handle_changes(self, corporate: Corporate, raw_text: str):
    #     log.debug(f"Changes are made to company: {corporate.id}")
    #     corporate.event_type = "update"
    #     corporate.status = Status.STATUS_ACTIVE
    #     corporate.information = raw_text
    #     self.producer.produce_to_topic(corporate=corporate)

    # def handle_deletes(self, corporate: Corporate):
    #     log.debug(f"Company {corporate.id} is inactive")
    #     corporate.event_type = "delete"
    #     corporate.status = Status.STATUS_INACTIVE
    #     self.producer.produce_to_topic(corporate=corporate)
