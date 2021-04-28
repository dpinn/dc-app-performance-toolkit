import random
import json

from selenium.webdriver.common.by import By
from selenium_ui.conftest import retry

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue, PopupManager
from selenium_ui.jira.pages.selectors import IssueLocators

from util.api.jira_clients import JiraRestClient
from util.conf import JIRA_SETTINGS

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()

def app_specific_action(webdriver, datasets):
    base_page = BasePage(webdriver)
    issue_modal = Issue(webdriver)

    def set_issue_type(issue_modal):
        issue_types = {}
        data_suggestions = json.loads(issue_modal.get_element(IssueLocators.issue_types_options)
                                      .get_attribute('data-suggestions'))
        for data in data_suggestions:
            # 'Please select' is label in items list where all issue types are presented (not for current project)
            if 'Please select' not in str(data):
                items = data['items']
                for label in items:
                    if label['label'] not in issue_types:
                        issue_types[label['label']] = label['selected']
        if 'Risk' in issue_types:
            if not(issue_types['Risk']):

                @retry(delay=0.25, backoff=1.5)
                def choose_risk_issue_type():
                    # Do in case of 'Risk' issue type is not selected
                    issue_modal.action_chains().move_to_element(issue_modal.get_element(IssueLocators.issue_type_field))
                    issue_modal.get_element(IssueLocators.issue_type_field).click()
                    issue_dropdown_elements = issue_modal.get_elements(IssueLocators.issue_type_dropdown_elements)
                    if issue_dropdown_elements:
                        risk_element = next((x for x in issue_dropdown_elements if x.text == 'Risk'), None)
                        issue_modal.action_chains().move_to_element(risk_element).click(risk_element).perform()
                    issue_modal.wait_until_invisible(IssueLocators.issue_ready_to_save_spinner)
                choose_risk_issue_type()

    def set_impact(issue_page):
        impact_field = issue_page.get_elements((By.ID, 'customfield_10112'))
        if impact_field:
            drop_down_length = len(issue_page.select(impact_field[0]).options)
            random_impact_id = random.randint(1, drop_down_length - 1)
            issue_page.select(impact_field[0]).select_by_index(random_impact_id)

    def set_probab(issue_page):
        probab_field = issue_page.get_elements((By.ID, 'customfield_10113'))
        if probab_field:
            drop_down_length = len(issue_page.select(probab_field[0]).options)
            random_probab_id = random.randint(1, drop_down_length - 1)
            issue_page.select(probab_field[0]).select_by_index(random_probab_id)

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:create_risk_issue")
        def create_risk_issue():
            issue_modal.open_create_issue_modal()
            issue_modal.fill_summary_create()  # Fill summary field
            issue_modal.fill_description_create(rte_status)  # Fill description field
            set_issue_type(issue_modal)  # Set issue type to Risk
            issue_modal.submit_issue()
            issue_modal.wait_until_clickable((By.ID, 'logo'))
        create_risk_issue()

        @print_timing("selenium_app_custom_action:edit_risk_assessment")
        def edit_risk_assessment():
            if datasets['custom_issues']:
                issue_id = datasets['custom_issue_id']
                issue_page = Issue(webdriver, issue_id=issue_id)
                issue_page.go_to_edit_issue()
                set_impact(issue_page)
                set_probab(issue_page)
                issue_page.edit_issue_submit()
                issue_page.wait_for_issue_title()
        edit_risk_assessment()

        @print_timing("selenium_app_custom_action:view_risk_register")
        def view_risk_register():
            base_page.wait_until_available_to_switch((By.ID, 'risk-assessment-iframe'))
            base_page.wait_until_clickable((By.ID, 'visit-risk-register'))
            base_page.get_element((By.ID, 'visit-risk-register')).click()
            base_page.return_to_parent_frame()
            base_page.wait_until_visible((By.CSS_SELECTOR, 'button[aria-controls="risk-register-menu"]'))
        view_risk_register()
    measure()

