# from django.test import LiveServerTestCase
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from django.contrib.auth.models import User
# from issues.models import Issue, Category, Response, Document
# from selenium.webdriver.support.ui import WebDriverWait
#
# class SeleniumTests(LiveServerTestCase):
#
#     fixtures = ['issues_test.json']
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = webdriver.Chrome()
#         cls.selenium.implicitly_wait(10)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
#
#
#     def test_login(self):
#
#         print("URL:",self.live_server_url)
#
#         issue=Issue.objects.get(id=1)
#         print(f'ISSUE: {issue.id},{issue.short_desc}, {issue.submitted_by.username}')
#
#         selenium = self.selenium
#         self.login_function(selenium)
#         import time
#         #time.sleep(5)
#
#         time.sleep(5)
#
#
#     def login_function(self,selenium):
#         #Opening the link we want to test
#         selenium.get(f'{self.live_server_url}/accounts/login/?next=/')
#         #find the form element
#         user = selenium.find_element_by_id('user')
#         password = selenium.find_element_by_id('password')
#         submit = selenium.find_element_by_class_name('btn')
#         #
#         # #Fill the form with data
#         user.send_keys('todd')
#         password.send_keys('todd0606')
#         submit.click()