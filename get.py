import time
import re
import pandas as pd


from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

def optout_cookies():
    try:
        # Attempt to find the element by ID
        optout_link = driver.find_element(By.ID, "optout_link")

        # If the element is found, click it
        optout_link.click()
        time.sleep(2)
    except Exception as e:
        print("Element with ID 'optout_link' not found")

def accept_cookies():
    try:
        # Attempt to find the element by ID
        accept_cookies = driver.find_element(By.CLASS_NAME, "btn.btn-grey.allow_all_btn.cs_action_btn")

        # If the element is found, click it
        accept_cookies.click()
        time.sleep(2)
    except Exception as e:
        # Handle the case when the element is not found
        print("Element with Class 'btn.btn-grey.allow_all_btn.cs_action_btn' not found")

def get_class_name_id(link):
    class_name = None
    id = None
    try:
        # Define the base URL of the page to scrape
        driver.get(link)
        optout_cookies()
        accept_cookies()
        print(link)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(e)
        return None, None

    regex = re.compile('.add.to.cart.|.addItemToCart.|.addtocart|addtocart.|addtocart|cart-button|.btn-cart-container.  ')
    for EachPart in soup.find_all("div", {"class": regex}):
        class_name = str(EachPart).split('class="')[1].split('"')[0]
        break

    regex = re.compile('.adca')
    for EachPart in soup.find_all("div", {"id": regex}):
        id = str(EachPart).split('id="')[1].split('"')[0]
        print(f'ID: {id}')
        break

    regex = re.compile('.add.to.cart.|.addItemToCart.|.addtocart|addtocart.|.basket.|(?<![\w\d])btn btn-primary(?![\w\d])|btn.btn-cart')
    for EachPart in soup.find_all("a", {"class": regex}):
        class_name = str(EachPart).split('class="')[1].split('"')[0]
        break

    regex = re.compile('.add.to.cart.|.addItemToCart.|.addtocart|addtocart.|addtocart')
    for EachPart in soup.find_all("input", {"class": regex}):
        class_name = str(EachPart).split('class="')[1].split('"')[0]
        break

    regex = re.compile('.add.to.cart.|.addItemToCart.|.addtocart|addtocart.|.cart.submit.|.cart|.addToBag.|.button-red btn-block.|.add-to-tote|btn.btn-succes')
    for EachPart in soup.find_all("button", {"class": regex}):
        class_name = str(EachPart).split('class="')[1].split('"')[0]
        break

    regex = re.compile('btnAddToBasket.')
    for EachPart in soup.find_all("button", {"id": regex}):
        id = str(EachPart).split('id="')[1].split('"')[0]
        print(f'ID: {id}')
        break

    return class_name, id


def get_colors(link, class_name, id):
    try:
        print(class_name)
        if class_name is not None:
            input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name.replace(' ', '.'))))
        else:
            input_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))

        # Get text of the input element
        text = input_element.text
        print("Text of the input element:", text)

        # Get background color of the input element
        bg_color = input_element.value_of_css_property("background-color")
        print("Background color:", bg_color)

        # Get text color (foreground color) of the input element
        text_color = input_element.value_of_css_property("color")
        print("Text color:", text_color)

        # Perform a hover action on the input element
        ActionChains(driver).move_to_element(input_element).perform()

        time.sleep(1)

        # Get background color of the input element after hovering
        bg_color_hover = input_element.value_of_css_property("background-color")
        print("Background hover:", bg_color_hover)

        return bg_color, text_color, bg_color_hover
    except Exception as e:
        print(f"Exception: Unable to find button with class name '{class_name}'")
        return None, None, None


service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()
# driver.implicitly_wait(20)  # gives an implicit wait for 20 seconds


df = pd.read_csv('colour_selector.csv')

dataframe = pd.DataFrame(columns=['storeUrl', 'button color', 'hover', 'text color'])

for index, row in df.iterrows():
    base = row['storeUrl']
    link = row['product url']
    class_name, id = get_class_name_id(link)
    color, text_color, hover = get_colors(link, class_name, id)

    new_row_dict = {'storeUrl': base, 'button color': color, 'text color': text_color, 'hover': hover}
    # Use len(dataframe) as the index to automatically assign the next available index
    dataframe.loc[len(dataframe)] = new_row_dict

print(dataframe.head(20))
dataframe.to_csv('results.csv', index=False)


time.sleep(5)

driver.quit()