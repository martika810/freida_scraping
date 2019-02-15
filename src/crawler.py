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
                    cleaned_item = self.extract_item_data(item)
                    item_serie = pd.Series(cleaned_item,index= cleaned_item.keys())

                    dataframe = dataframe.append(item_serie, ignore_index=True, sort=False)
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

    def extract_item_data(self, item_dict):
        self.browser.get("https://freida.ama-assn.org/Freida/user/programDetails.do?pgmNumber={0}".format(item_dict['pgmNbr']))
        item_detailed_json_data = self.loadJsonContent(self.browser.page_source)
        cleaned_dictionary = {}
        cleaned_dictionary["Program Name"] = self.extract_field(item_detailed_json_data,'pgmNm')
        cleaned_dictionary["Program Id"] = self.extract_field(item_detailed_json_data,'pgmNbr')
        cleaned_dictionary["Location"] = self.extract_field(item_detailed_json_data,'city') + "," +self.extract_field(item_dict,'stateCd')
        cleaned_dictionary["Speciality"] = self.extract_field(item_detailed_json_data,'spcDescText')
        cleaned_dictionary["Last Updated"] = self.extract_field(item_detailed_json_data,'lastUpdated')
        cleaned_dictionary["Program Director Info"] = self.extract_field(item_detailed_json_data,'programDirectorInfo')
        cleaned_dictionary["Program Person to Contact"] = self.extract_field(item_detailed_json_data,'programContactInfo')
        cleaned_dictionary["Website"] =self.extract_field(item_detailed_json_data,'website')
        cleaned_dictionary["Accredited Length Training"] = self.extract_field(item_detailed_json_data,'pgmAccLength')
        cleaned_dictionary["Required Length"] = self.extract_field(item_detailed_json_data,'pgmLength')
        cleaned_dictionary["Program Start Date"] = self.extract_field(item_detailed_json_data,'startDate')
        cleaned_dictionary["Participates in Eras"] = self.extract_field(item_detailed_json_data,'eras')
        cleaned_dictionary["Affiliated US Government"] = self.extract_field(item_detailed_json_data,'pgmGovAffilInd')

        #raw: "010519:Brookwood Baptist Health-Birmingham, AL",
        sponsor_info = ''
        for sponsor_text in self.extract_field(item_detailed_json_data,'sponsorInfo').split('|'):
            if(sponsor_text.find(':')>-1):
                sponsor_info = sponsor_info + sponsor_text.split(':')[1] + '|'
            else:
                sponsor_info = sponsor_text
        cleaned_dictionary["Sponsor Info"] = sponsor_info

        # raw "010307:Grandview Medical Center-Vestavia Hills, AL|010187:Princeton Baptist Medical Center-Birmingham, AL"
        participant_info= ''
        for participant_text in self.extract_field(item_detailed_json_data,'participantInfo').split('|'):
            if(participant_text.find(':')>-1):
                participant_info = participant_info + participant_text.split(':')[1] + '|'
            else:
                participant_info = participant_text
        cleaned_dictionary["Participant Info"] = participant_info

        total_program_size = ''
        for work_per_year in self.extract_field(item_detailed_json_data,'workScheduleList'):
            if(work_per_year!=""):
                total_program_size = "Year " + work_per_year["yrCd"] + '| Position '+work_per_year["pryYrQtyPositions"] + ';'
            else:
                total_program_size = ''

        cleaned_dictionary["Total Program Size"] = total_program_size
        cleaned_dictionary["Primary Teaching Site"] = self.extract_field(item_detailed_json_data,"primaryTeachingSite")
        cleaned_dictionary["Program Best Described as"] = self.extract_field(item_detailed_json_data,"pgmType")
        cleaned_dictionary["Requires previous GME"] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppGmeRqdInd")
        cleaned_dictionary["Offers preliminary positions"] = self.extract_field(item_detailed_json_data,"preliminaryPositionsAvailable")
        cleaned_dictionary["Average Level 1 Score Of Current Residents"] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgComlexLvl1Score')
        cleaned_dictionary["J1 Visa Sponsorship"] = self.extract_field(item_detailed_json_data,"j1Visa")
        cleaned_dictionary["H1B Visa"] = self.extract_field(item_detailed_json_data,"h1bVisa")
        cleaned_dictionary["F1 Visa(Opt 1st year)"] = self.extract_field(item_detailed_json_data,"f1Visa")
        cleaned_dictionary["% USMD"] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgUSMD')
        cleaned_dictionary["% IMG"] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgImg')
        cleaned_dictionary["% DO"] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgDo')
        cleaned_dictionary['% FEMALE'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgFemale')
        cleaned_dictionary['% MALE'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgMale')
        cleaned_dictionary['Participates Main Match of the National Resident '] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppNrmpCodeDisplay')
        cleaned_dictionary['Participates Advanced or Fellowship Match of the '] = "No" if self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppAdvancedMatchInd")=="N" else "Yes"
        cleaned_dictionary['Participant in San Francisco match']= "No" if self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppSfMatch') == "0" else "Yes"
        cleaned_dictionary['Participant in another matching program']= "No" if self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppOthMatchInd")=="0" else "Yes"
        cleaned_dictionary['Interviews conducted last year for first year positions']= self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppInterviewed")
        cleaned_dictionary['Applicants may interview remotely via video conferencing']= "No" if self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppInterRemote")=="0" else "Yes"
        cleaned_dictionary['Osteopathic Recognition accredited by the ACGME and the AOA'] = "No" if self.extract_field(item_detailed_json_data,'jsonExpandedProgram',"xppAcrdAoaInd")=="0" else "Yes"
        cleaned_dictionary['USMLE Step 1 Required'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppUsmleStep1Ind')
        cleaned_dictionary['USMLE Step 1 Minimum Score'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppUsmleStep1Score')
        cleaned_dictionary['USMLE Step 2 Required'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppUsmleStep2Ind')
        cleaned_dictionary['USMLE Step 2 Minimum Score'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppUsmleStep2Score')
        cleaned_dictionary['Average Step 1 Score Current Residents'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppAvgUsmleStep1Score')
        cleaned_dictionary['Complex Level 1 Required for interview considerations(DOs only)'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppComlexLvl1Ind')
        cleaned_dictionary['Complex Level 1 Minimum Score for interview considerations(DOs only)'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppComlexLvl1Score')
        cleaned_dictionary['Complex Level 2 Required for interview considerations(DOs only)'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppComlexLvl2Ind')
        cleaned_dictionary['Complex Level 2 Minimum Score for interview considerations(DOs only)'] = self.extract_field(item_detailed_json_data,'jsonExpandedProgram','xppComlexLvl2Score')

        return cleaned_dictionary

    def extract_field(self, dictionary, first_field_name, second_field_name = None):
        try:
            if not second_field_name:
                return dictionary[first_field_name]
            else:
                return dictionary[first_field_name][second_field_name]
        except Exception as e:
            print(str(e))
            return ""