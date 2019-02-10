
class FreidaConfig:

    next_button_css_selector = 'a.ama__pagination__next'
    total_number_items_selector = 'div.results small'

    #If the page has popup
    is_there_popup_question_beginning = True
    question_yes_button = '#agreeBtn span.ui-button-text'
    is_there_cookies_question_beginning = False
    agree_use_cookies = ''
    initial_page = "https://freida.ama-assn.org/Freida/user/search/programSearchSubmit.do?specialtiesToSearch=140"
    host= 'https://freida.ama-assn.org/'


    def __init__(self,browser):
        self.browser = browser

    def answer_prompt_questions(self):
        if(self.is_there_popup_question_beginning):
            self.answer_yes_to_popup_question()


    def answer_yes_to_popup_question(self):
        yes_button = self.browser.find_element_by_css_selector(self.question_yes_button)
        yes_button.click()
        self.is_there_popup_question_beginning = False





