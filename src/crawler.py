from pathlib import Path
import pandas as pd
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urljoin
from src.progress import Progress


class Crawler:
    def __init__(self,browser,config):
        self.browser = browser
        self.config = config

    def crawl_all_pages_to_end(self,initial_url,file_to_save_results):


        try:
            url_first_load = initial_url
            self.browser.get("https://freida.ama-assn.org/Freida/#/programs?program=residencies&specialtiesToSearch=140")
            self.config.answer_prompt_questions()

            # Wait for page to load
            wait = WebDriverWait(self.browser, 10, ignored_exceptions = [StaleElementReferenceException,NoSuchElementException])
            items_presence = EC.presence_of_element_located((By.CSS_SELECTOR,self.config.next_button_css_selector))
            wait.until(items_presence)

            self.browser.execute_script('window.open("'+url_first_load+'");')

            # Swith to new tab
            self.browser.switch_to.window(self.browser.window_handles[1])

            # Create dataframe to hold the data
            dataframe_file = Path(file_to_save_results)
            if(not dataframe_file.exists()):
                dataframe = pd.DataFrame()
            else:
                dataframe = pd.read_csv(file_to_save_results)

            jsonData = self.loadJsonContent(self.browser.page_source)

            progress = Progress()

            total_number_items = self.total_number_items_to_scrape(jsonData)
            progress.save_total_number_items(total_number_items)
            progress.save_process_progress(False,False)

            for pagination_item in jsonData['solrPagination']:

                url_to_parse = urljoin(self.config.host, pagination_item["url"])
                self.browser.get(url_to_parse)
                page_json_data = self.loadJsonContent(self.browser.page_source)

                for item in page_json_data["searchResults"]:
                    cleaned_item = self.clean_item(item)
                    item_serie = pd.Series(cleaned_item,index= cleaned_item.keys())

                    dataframe = dataframe.append(item_serie, ignore_index=True)
                    progress.save_number_items_scraped_so_far(dataframe.shape[0])
                    progress.add_item_scraped(cleaned_item)
                    progress.save_process_progress(False,False)

                dataframe.to_csv(file_to_save_results)

            progress.save_process_progress(True,False)
            return True
        except Exception as e:
            print(str(e))
            progress.save_process_progress(True,True)
            return False

    def loadJsonContent(self,html_page):
        html_parser = BeautifulSoup(html_page, 'html.parser')
        json_data = json.loads(html_parser.find('pre').text)
        return json_data

    def total_number_items_to_scrape(self,json_dict):
        return json_dict["numberFound"]
    def scrape(self, initial_url, file_to_save_results):
        print("Start crawling...")

        got_to_end = self.crawl_all_pages_to_end(initial_url,file_to_save_results)
        if(got_to_end):
            print('Scraping finished successfully')
        else:
            print("Error during scraping")

        print("Finish crawling...")

    def clean_item(self, item_dict):
        cleaned_dictionary = {}
        cleaned_dictionary["Program Name"] = item_dict['pgmNm']
        cleaned_dictionary["Program Id"] = item_dict['pgmNbr']
        cleaned_dictionary["Location"] = item_dict['stateNm'] + "," +item_dict['stateCd']
        return cleaned_dictionary