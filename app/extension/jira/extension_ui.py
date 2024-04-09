import random

from selenium.webdriver.common.by import By
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue

from util.api.jira_clients import JiraRestClient
from util.conf import JIRA_SETTINGS

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()

def app_specific_action(webdriver, datasets):
    base_page = BasePage(webdriver)

    def set_impact(issue_page):
        impact_field = issue_page.get_elements((By.ID, 'customfield_11100'))
        if impact_field:
            drop_down_length = len(issue_page.select(impact_field[0]).options)
            random_impact_id = random.randint(1, drop_down_length - 1)
            issue_page.select(impact_field[0]).select_by_index(random_impact_id)

    def set_probab(issue_page):
        probab_field = issue_page.get_elements((By.ID, 'customfield_11101'))
        if probab_field:
            drop_down_length = len(issue_page.select(probab_field[0]).options)
            random_probab_id = random.randint(1, drop_down_length - 1)
            issue_page.select(probab_field[0]).select_by_index(random_probab_id)

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("selenium_app_custom_action:edit_risk_assessment")
        def edit_risk_assessment():
            issue_page.go_to_edit_issue()
            set_impact(issue_page)
            set_probab(issue_page)
            issue_page.edit_issue_submit()
            issue_page.wait_for_issue_title()

        @print_timing("selenium_app_custom_action:view_risk_register")
        def view_risk_register():
            base_page.wait_until_available_to_switch((By.ID, 'risk-assessment-iframe'))
            base_page.wait_until_clickable((By.ID, 'visit-risk-register'))
            base_page.get_element((By.ID, 'visit-risk-register')).click()
            base_page.return_to_parent_frame()
            base_page.wait_until_visible((By.CSS_SELECTOR, 'button[aria-controls="risk-register-menu"]'))

        if datasets['custom_issues']:
            issue_id = datasets['custom_issue_id']
            issue_page = Issue(webdriver, issue_id=issue_id)
            edit_risk_assessment()
            view_risk_register()
    measure()

