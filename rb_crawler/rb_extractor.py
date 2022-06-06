import logging
from time import sleep

import requests
from parsel import Selector

from build.gen.bakdata.corporate.v2.corporate_pb2 import Corporate
from build.gen.bakdata.announcement.announcement_pb2 import Announcement, Status
from rb_producer_c import RbProducerC
from rb_producer_a import RbProducerA

import re

log = logging.getLogger(__name__)


class RbExtractor:
    def __init__(self, start_rb_id: int, state: str):
        self.rb_id = start_rb_id
        self.state = state
        self.producer_c = RbProducerC()
        self.producer_a = RbProducerA()

    def extract(self):
        while True:
            try:
                log.info(f"Sending Request for: {self.rb_id} and state: {self.state}")
                text = self.send_request()
                if "Falsche Parameter" in text:
                    log.info("The end has reached")
                    break
                selector = Selector(text=text)
                corporate = Corporate()
                announcement = Announcement()
                announcement.rb_id = self.rb_id
                announcement.state = self.state
                corporate.reference_id = self.extract_company_reference_number(selector)
                announcement.reference_id = self.extract_company_reference_number(selector)
                event_type = selector.xpath("/html/body/font/table/tr[3]/td/text()").get()
                announcement.event_date = selector.xpath("/html/body/font/table/tr[4]/td/text()").get()
                corporate.id = f"{self.state}_{self.rb_id}"
                announcement.id = f"{self.rb_id}_{self.state}"
                raw_text: str = selector.xpath("/html/body/font/table/tr[6]/td/text()").get()
                self.handle_corporates(corporate, raw_text)
                self.handle_events(announcement, event_type, raw_text)
                self.rb_id = self.rb_id + 1
                log.debug(corporate)
            except Exception as ex:
                log.error(f"Skipping {self.rb_id} in state {self.state}")
                log.error(f"Cause: {ex}")
                self.rb_id = self.rb_id + 1
                continue
        exit(0)

    def send_request(self) -> str:
        url = f"https://www.handelsregisterbekanntmachungen.de/skripte/hrb.php?rb_id={self.rb_id}&land_abk={self.state}"
        # For graceful crawling! Remove this at your own risk!
        sleep(0.5)
        return requests.get(url=url).text

    @staticmethod
    def extract_company_reference_number(selector: Selector) -> str:
        return ((selector.xpath("/html/body/font/table/tr[1]/td/nobr/u/text()").get()).split(": ")[1]).strip()

    def handle_events(self, announcement, event_type, raw_text):
        if event_type == "Neueintragungen":
            self.handle_new_entries(announcement, raw_text)
        elif event_type == "Veränderungen":
            self.handle_changes(announcement, raw_text)
        elif event_type == "Löschungen":
            self.handle_deletes(announcement)
            
    # extract information from raw_text
    # needs modifications for other states than bw
    def handle_corporates(self, corporate: Corporate, raw_text: str) -> Corporate:
        search_name = '^\"?(.*?)\"?,\s([A-zÜüÖöÄä-]+?[^A-Z]\s)*?\('
        search_address1 = '.*?\((.+?,\s\d{5}\s.+?)[,\)].*\.'
        search_address2 = '.*?\((.+?)\)\.'
        search_address3 = '(.*?),\s(\d+)\s(.*)'
        search_address4 = '(\d+)\s(.*)'
        search_capital = 'Stammkapital:\s(.*?EUR)'
        search_industry1 = '.*?\(.+?,\s\d{5}\s.+?,\s?(.*?)?\.?\)\.'
        search_industry2 = 'Gegenstand:\s([Ss]ind\s)?([Ii]st\s)?(.*?)\.\s[A-ZÖÄÜ]'
        search_ceo = '[^r][\s\.]Geschäftsführer(in)?:\s([^:]*?\d{4})[,\.]'
        search_ceo_name = '(.*?),[^,]*?,[^,]*?\d'
        #replace_text = '.*?\)\.\s?'
        
        if re.search(search_name, raw_text):
            corporate.name = re.search(search_name, raw_text).group(1)
        else:
            pass
        
        if re.search(search_address1, raw_text):
            address = re.search(search_address1, raw_text).group(1)
        elif re.search(search_address2, raw_text):
            address = re.search(search_address2, raw_text).group(1)
        else:
            pass
            
        if re.search(search_address3, address):
            corporate.street = re.search(search_address3, address).group(1)
            corporate.postal_code = re.search(search_address3, address).group(2)
            corporate.city = re.search(search_address3, address).group(3)
        elif re.search(search_address4, address):
            corporate.postal_code = re.search(search_address4, address).group(1)
            corporate.city = re.search(search_address4, address).group(2)
        else:
            corporate.city = address
        
        if re.search(search_capital, raw_text):
            corporate.capital = re.search(search_capital, raw_text).group(1)
        else:
            pass
        
        if re.search(search_industry1, raw_text):
            corporate.industry_description = re.search(search_industry1, raw_text).group(1)
        elif re.search(search_industry2, raw_text):
            corporate.industry_description = re.search(search_industry2, raw_text).group(3)
        else:
            pass
        
        if re.search(search_ceo, raw_text):
            ceos = []
            result = re.search(search_ceo, raw_text).group(2).split('; ')
            iter_len = len(result)
            for e in range(iter_len):
               ceos.append(re.search(search_ceo_name, result[e]).group(1))
            corporate.ceo[:] = ceos
        else:
            pass
        
        #raw_text = re.sub(replace_text, '', raw_text)
        self.producer_c.produce_to_topic(corporate=corporate)

    def handle_new_entries(self, announcement: Announcement, raw_text: str) -> Announcement:
        log.debug(f"New company found: {announcement.id}")
        announcement.event_type = "create"
        announcement.information = raw_text
        announcement.status = Status.STATUS_ACTIVE
        self.producer_a.produce_to_topic(announcement=announcement)

    def handle_changes(self, announcement: Announcement, raw_text: str):
        log.debug(f"Changes are made to company: {announcement.id}")
        announcement.event_type = "update"
        announcement.status = Status.STATUS_ACTIVE
        announcement.information = raw_text
        self.producer_a.produce_to_topic(announcement=announcement)

    def handle_deletes(self, announcement: Announcement):
        log.debug(f"Company {announcement.id} is inactive")
        announcement.event_type = "delete"
        announcement.information = ""
        announcement.status = Status.STATUS_INACTIVE
        self.producer_a.produce_to_topic(announcement=announcement)
