import argparse
import winsound
from uiautomator2 import Device
import Variables.EnvVariables as Env
import Resources.PO as PageObjects
import time

from selenium import webdriver
from selenium.webdriver import ActionChains


loopCount = 0
try:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-m", "--MobileNum", required=False, help="Please Provide your Mobile No to receive OTP")
    argparser.add_argument("-d", "--DeviceID", required=False,
                           help="Please Provide your DeviceID to retrieve OTP from your mobile")
    args = vars(argparser.parse_args())
    if args["DeviceID"] != "":
        d = Device(args["DeviceID"])
    else:
        print("Taking the device id from environment variables")
        d = Device(Env.DeviceID)  # Connecting to the device for the getting the OTP
except Exception:
    d = None
    print("Device is either offline or not connected through USB")


if Env.BrowserType.lower() == "chrome":
    driver = webdriver.Chrome(executable_path="..\\Resources\\chromedriver.exe")
elif Env.BrowserType.lower() == 'firefox':
    driver = webdriver.Chrome(executable_path="..\\Resources\\geckodriver.exe")


driver.get(Env.BrowserURL)
driver.maximize_window()
driver.find_element_by_css_selector(PageObjects.EnterMobileNoInput_CSSSel).send_keys(Env.MobileNum)
driver.find_element_by_xpath(PageObjects.GetOTPButton_XPath).click()
time.sleep(10)
try:
    if d != None:
        d.screen_on()
        d.press('home')
        d(text="Messages").click()
        time.sleep(3)
        otpSender = d(index=0).child(resourceIdMatches='com.google.android.apps.messaging:id/conversation_name').get_text()
        otp = d(index=0).child(resourceIdMatches='com.google.android.apps.messaging:id/conversation_snippet').get_text()
        print(otp)
        d.press("back")
        if "AX-NHPSMS" == otpSender:
            otpprocesssed = otp.split("Your OTP to register/access CoWIN is ")[1].replace(". It will be valid for 3 minutes. - CoWIN","")
    else:
        print("PLEASE ENTER OTP MANUALLY")
        time.sleep(30)

    driver.find_element_by_css_selector(PageObjects.EnterOTPInput_CSSSel).send_keys(otpprocesssed)
except Exception:
    print("Either Device is not available or OTP is not generated")

driver.find_element_by_xpath(PageObjects.VerifyProceedButton_XPath).click()
time.sleep(5)
driver.find_element_by_xpath(PageObjects.ScheduleButton_XPath).click()
time.sleep(2)
if Env.SearchBy.lower() == "district":
    driver.find_element_by_css_selector(PageObjects.SearchByDistrict_CSSSel).click()
    time.sleep(2)
    driver.find_element_by_id("mat-select-0").click()
    driver.find_element_by_xpath("//span[contains(text(),'" + Env.StateID + "')]").click()
    time.sleep(2)
    driver.find_element_by_id("mat-select-2").click()
    driver.find_element_by_xpath("//span[contains(text(),'" + Env.DistrictID + "')]").click()
else:
    # driver.find_element_by_css_selector(PageObjects.SearchByPIN_CSSSel).click()
    time.sleep(1)
    driver.find_element_by_id("mat-input-10").send_keys(Env.PINCODE)
time.sleep(2)


foundSlot = 0
while foundSlot == 0:
    driver.find_element_by_xpath(PageObjects.SearchButton_XPath).click()
    time.sleep(1)

    if (Env.Age >= 18 and Env.Age < 45):
        driver.find_element_by_xpath("//label[contains(text(),'Age 18+')]").click()
    elif Env.Age >= 45:
        # driver.find_element_by_xpath("//label[contains(text(),'Age 45+')]").click()
        driver.find_element_by_css_selector("label[text='Age 45+']").click()
    time.sleep(1)

    ele = driver.find_element_by_xpath("//mat-selection-list[@formcontrolname='center_id']")
    rows = driver.find_elements_by_xpath(".//div[@class='row-disp']")
    avl_dates = driver.find_elements_by_xpath("//div/li[@class='availability-date']")
    for row in rows:
        row_cols = row.find_elements_by_xpath("..//..//a[@href='/appointment']")
        # for child,avl_date in zip(row_cols,avl_dates): ---  commented as we need any date
        for child in row_cols:
            if child.text.isdigit():
                # cur_date = avl_date.text  --- commented as we need any date
                print(row.text)
                print(child.text)
                # print(cur_date)   ----  commented as we need any date
                print("\n")
                # if cur_date == Env.VaccinationDate:  --- commented as we need any date
                if ',' in Env.HospitalName:
                    hosarr = Env.HospitalName.split(',')
                    for ele in hosarr:
                        if ele.lower() in row.text.lower():
                            actions = ActionChains(driver)
                            actions.move_to_element(child).click().perform()
                            # child.click()
                            l = driver.find_elements_by_css_selector("[role='alertdialog']")
                            # check condition, if list size > 0, element exists
                            if (len(l) > 0):
                                print("PLEASE NOTE - " +  l[0].text)
                            foundSlot = 1
                            break
                    if foundSlot == 1:
                        break
                else:
                    if Env.HospitalName.lower() in row.text.lower():
                        actions = ActionChains(driver)
                        actions.move_to_element(child).click().perform()
                        # child.click()
                        l = driver.find_elements_by_css_selector("[role='alertdialog']")
                        # check condition, if list size > 0, element exists
                        if (len(l) > 0):
                            print("PLEASE NOTE - " + l[0].text)

                        foundSlot = 1
                        break

        if foundSlot == 1:
            break
    if foundSlot == 0:
        loopCount = loopCount + 1
        if loopCount == 30 :
            foundSlot = 1
        print("Continuing the Loop")
        time.sleep(30)


slots = driver.find_elements_by_class_name("time-slot-list")

if len(slots) > 0:
    slots[0].click()
    frequency = 1000  # Set Frequency To 2500 Hertz
    duration = 10000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)


# driver.close()

