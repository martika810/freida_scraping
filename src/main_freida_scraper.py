
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.crawler import Crawler
from src.freida_config import FreidaConfig
import time
from src.progress import Progress


def main(browser,url, config):

    crawler = Crawler(browser, FreidaConfig(browser))
    crawler.scrape(url, 'freida_results_'+ str(time.time())[:10] +'.csv')

def setup_browser():
    # Set up the selenium browser
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')

    prefs = {"profile.default_content_setting_values.geolocation" :2}
    options.add_experimental_option("prefs",prefs)

    browser = webdriver.Chrome('./chromedriver', chrome_options=options)
    browser.implicitly_wait(25)
    return browser

def run_freida_scraping():
    try:
        progress = Progress()
        progress.init()
        progress.save_process_progress(False,False)
        browser = setup_browser()
        config = FreidaConfig(browser)
        url = config.initial_page
        main(browser, url, config)
        browser.quit()
    except Exception:
        if browser:
            browser.quit()

if __name__ == '__main__':

    initial_url = "https://freida.ama-assn.org/Freida/user/search/programSearchSubmit.do?specialtiesToSearch=140"
    browser = setup_browser()
    config = FreidaConfig(browser)

    main(browser, initial_url, config)
    browser.quit()