from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

FIRST = "https://my.arlo.com/?_ga=2.72087187.1057132506.1558461222-1738443716.1558191218#/login"

def get_url_selenium():
	profile = webdriver.FirefoxProfile()
	profile.set_preference("plugin.state.flash", 2)
	driver = webdriver.Firefox(profile)
	print
	print("There is a way to wait until an item loads, \
	look it up and use it intead of the time.sleep() - \
	it will shorten the waiting time and avoid errors.")
	driver.get(FIRST)
	elem = driver.find_element_by_name("userId")
	elem.send_keys("royzohar25@gmail.com")

	elem = driver.find_element_by_name("password")
	elem.send_keys("1Qazwsxdcv")

	elem.send_keys(Keys.RETURN)

	time.sleep(20)

	elem = driver.find_element_by_id("cameras_play_idle_51D28573A1683")
	elem.click()

	time.sleep(20)

	elem = driver.find_element_by_id("cameras_cameraSnapshot_51D28573A1683")
	elem.click()

	elem = driver.find_element_by_id("footer_library")
	elem.click()

	time.sleep(5)

	try:
		elem = driver.find_element_by_id("modal_close")
		elem.click()
	except Exception as e:
		print(e)
		pass

	time.sleep(5)

	url = driver.find_element_by_xpath(
		"//div[@id='day_record_0']//a//img"
	).get_attribute("src")

	driver.close()
	driver.quit()

	return url