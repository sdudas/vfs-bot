from selenium import webdriver
import urllib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from twilio.rest import Client
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from twocaptcha import TwoCaptcha

## VFS login email
email_str = 'VFS EMAIL USERNAME'

## VFS password
pwd_str = 'VFS PORTAL PASSWORD'

## From Visa application - starts with GWF
gwf_nbr = 'GWF NUMBER'

'''
I used the Twilio python API to be able to text myself with appointment alerts!
Twilio id, auth token, and twilio assigned phone number from Twilio free profile
For help, check out https://www.twilio.com/docs/libraries/python.
'''
account_sid = 'TWILIO SID'
auth_token = 'TWILIO AUTH TOKEN'
twilio_client = Client(account_sid, auth_token)
twilio_phone = 'TWILIO PHONE NUMBER'
## Replace this here with the phone number you'd like to recieve SMS at
my_phone = 'MY PHONE NUMBER'

'''
2Capcha is used to outsource solving the capchas - pay 50 cents / 1000 capchas solved.
Load 50 cents for an account and insert your api key below.
For help, check out https://github.com/athre0z/twocaptcha-api.
'''
two_capcha_key = 'TWO CAPCHA API KEY'

no_appts = 'there are no appointments available at your chosen Visa Application Centre'


def log_msg(log, message):
	now = datetime.now()
	date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
	log.write(date_time + "  ::  " + message + "\n")

def login(browser, solver, log):
	## Login Page
	browser.get(('https://myappointment.vfsglobal.co.uk/MyAppointment/?q=eDhlWnRkOWh4dVRlb2R3UEtiS0dSSUE0MnluVGN4aERMSk5MNHBWZEJNMjBCRVVyYTlZQ1IvL2JQYWRRQU1xczd1dWtvSVRFV0pidFh1NEpUK29FbFBOVStTQ1ZRT25QdTN2S1c3TU9DTllMdHpaclNSdDgxOUd0R1ZwTWJ0Vkc%3D'))
	browser.find_element_by_name('Email').send_keys(email_str)
	browser.find_element_by_name('Password').send_keys(pwd_str)
	## Solves the CAPCHA
	capcha_img = browser.find_element_by_id('CaptchaImage')
	src = capcha_img.get_attribute('src')
	with open('capcha.png', 'wb') as file:
		file.write(capcha_img.screenshot_as_png)
	log_msg(log, "About to attempt to solve with 2Capcha.")
	capcha = solver.normal('capcha.png', minLength=5, maxLength=5)
	browser.find_element_by_name('CaptchaInputText').send_keys(capcha['code'])
	browser.find_element_by_class_name('btn-primary').click()
	log_msg(log, "Logged in with capcha " + capcha['code'])
	## My applications page
	browser.find_element_by_name('Applicant.GwfNumber').send_keys(gwf_nbr)
	browser.find_element_by_name('Applicant.EmailAddress').send_keys(email_str)
	browser.find_element_by_name('submitbtn').click()

def alert_for_appointment(browser, log):
	## Returns a tuple, (Session expired, AppointmentAvailable)
	time.sleep(3)
	## Switches over to the new tab with appointment availability.
	browser.switch_to_window(browser.window_handles[1])
	browser.save_screenshot("appointmentImage.png")
	if (no_appts not in browser.page_source):
		if check_session_expired(browser, log):
			browser.close()
			browser.switch_to_window(browser.window_handles[0])
			return (True, False)
		log_msg(log, "FOUND APPOINTMENTS!")
		browser.save_screenshot("appointmentImage.png")

		message = twilio_client.messages\
			.create(
				body = 'THERE ARE APPOINTMENTS!! AHH!!',
				from_= twilio_phone, 
				to= my_phone)
		return (check_session_expired(browser, log), True)
	else:
		log_msg(log, "No appointments available.")
	browser.close()
	browser.switch_to_window(browser.window_handles[0])
	return (check_session_expired(browser, log), False)

def check_appointment(browser, log):
	## Returns a tuple, (Session expired, AppointmentAvailable)
	time.sleep(2)
	if check_session_expired(browser, log):
		return (True, False)
	browser.find_element_by_id('Documentupload').click()
	continue_btn = browser.find_element_by_id('btn_continue')
	'''
	This is the action keys to right click on the continue button
	(to open the resulting page in a new tab).  You'd need to change
	this action sequence if you're not on a Mac.
	'''
	ActionChains(browser) \
	   	.key_down(Keys.COMMAND) \
	   	.click(continue_btn) \
	   	.key_up(Keys.COMMAND) \
	   	.perform()
	return alert_for_appointment(browser, log)

def check_session_expired(browser, log):
	if 'Session timeout' in browser.page_source:
		log_msg(log, "Session expired.")
		return True
	return False

def monitor_appointments():
	## Potentially change this path for wherever you have installed the chromedriver.
	browser = webdriver.Chrome(executable_path='/Users/sofia/dev/chromedriver')
	solver = TwoCaptcha(two_capcha_key)
	log = open('vfslog.txt', 'w+')
	appointments = False
	while True:
		login(browser, solver, log)
		while not appointments:
			(expired, appointments) = check_appointment(browser, log)
			if expired:
				break
		if appointments:
			return

monitor_appointments()
