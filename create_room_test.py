# This is a automated script for creating and join a room
# Room name : test_room_A
# Username : tester1
# Answer: print("hello")

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# This will give you an webdriver location error. For Ubuntu,
# download the webdriver and move it to path /usr/local/bin
driver = webdriver.Chrome()
driver.get("http://127.0.0.1:5000/")

#----------------------SPLASH PAGE ----------------------#

room_name_field = driver.find_element_by_id("room_name_create")
room_name_field.clear()
room_name_field.send_keys("test_room_A")
room_name_field = driver.find_element_by_id("createRoom_button")
room_name_field.send_keys(Keys.RETURN)


#----------------------CREATE ROOM PAGE ----------------------#

print("Transitioned to CREATE ROOM PAGE")
room_description_field = driver.find_element_by_id("room_title")
room_description_field.send_keys("This is test room A")
question_field = driver.find_element_by_id("question")
question_field.send_keys("print hello")
answer_field = driver.find_element_by_id("answer")
answer_field.send_keys("hello")
submit_button = driver.find_element_by_tag_name("input")
submit_button.send_keys(Keys.RETURN)


#----------------------SPLASH PAGE ----------------------#

print("Transitioned to SPLASH PAGE")
username_field = driver.find_element_by_id("username")
username_field.clear()
username_field.send_keys("tester1")
roomname_field = driver.find_element_by_id("roomname")
roomname_field.send_keys("test_room_A")
room_name_field = driver.find_element_by_id("joinRoom_button")
room_name_field.send_keys(Keys.RETURN)


#----------------------JOIN ROOM PAGE ----------------------#

# I'm not sure how to access the textarea in CodeMirror so I will leave it here at this point



#driver.close()
