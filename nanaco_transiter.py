#!/usr/bin/env python3
import time
import re
from sys import argv
import selenium
from selenium import webdriver

userName = "" # <- 購入した福利厚生のIDを6桁と4桁で入力してください(例: 012345-6789)
nanacoNo = "" # <- nanaco番号16桁を入力してください(例: 0123456789012345)
securityCode = "" # <- カード記載の番号を7桁で入力してください(例: 0123456)

def getGiftCodes(driver, url):
    driver.get(url)
    driver.find_element_by_name("kainno").send_keys(userName)
    driver.find_element_by_class_name("next").click()
    elements = driver.find_elements_by_css_selector(".table_gift tbody tr")
    giftCodes = []
    for element in elements:
        texts = element.text.split(" ")
        if re.match("^[a-zA-Z\d]{16}$", texts[-3]):
            giftCodes.append(texts[-3])
    return giftCodes

# nanacoサイトのセッションを張る
def loginNanaco(driver):
    driver.get('https://www.nanaco-net.jp/pc/emServlet')
    driver.find_element_by_name("XCID").send_keys(nanacoNo)
    driver.find_element_by_name("SECURITY_CD").send_keys(securityCode)
    driver.find_element_by_name("ACT_ACBS_do_LOGIN2").click() # ここでログイン
    time.sleep(1)
    driver.find_element_by_link_text("nanacoギフト登録").click()
    time.sleep(1)

# セッション内でギフトコードを登録する
def registGiftCode(driver, code):
    driver.find_element_by_xpath("//input[@alt=\"ご利用約款に同意の上、登録\"]").click() # ここで新規ウィンドウが開く
    time.sleep(0.3)
    driver.switch_to.window(driver.window_handles[1]) # 直前に開いた新規ウィンドウをカレントにする

    driver.find_element_by_id("gift01").send_keys(code[:4])
    driver.find_element_by_id("gift02").send_keys(code[4:8])
    driver.find_element_by_id("gift03").send_keys(code[8:12])
    driver.find_element_by_id("gift04").send_keys(code[12:])

    driver.find_element_by_id("submit-button").click()
    time.sleep(0.1)
    result = True
    try:
        driver.find_element_by_xpath("//input[@alt=\"登録する\"]").click()
    except selenium.common.exceptions.NoSuchElementException:
        # 10秒以上経っても「登録する」ボタンが出てこない場合、タイムアウトとする
        result = False
    time.sleep(0.1)
    driver.close() # カレントウィンドウ(さっき開いた新規ウィンドウ)を閉じる
    driver.switch_to.window(driver.window_handles[0]) # nanacoページのウィンドウをカレントにする
    return result

if __name__ == "__main__":
    print("Preparing...")
    driver = selenium.webdriver.Chrome()
    driver.set_page_load_timeout(10)
    print("Getting gift codes ...")
    giftCodes = []
    for url in argv[1:]:
        giftCodes += getGiftCodes(driver, url)
    print("Logging in nanaco website ...")
    loginNanaco(driver)
    sucseeded = 0
    missed = 0
    print("Registing codes ...")
    for giftCode in giftCodes:
        print(giftCode, "...", end = "\r")
        if registGiftCode(driver, giftCode):
            sucseeded += 1
            print(giftCode, "(%d/%d)" % (sucseeded + missed, len(giftCodes)), "Done")
        else:
            missed += 1
            print(giftCode, "(%d/%d)" % (sucseeded + missed, len(giftCodes)), "MISSED\a")
    print("Sucseeded:", sucseeded, "    Missed:", missed, "    Total:", sucseeded + missed)
    driver.find_element_by_id("memberInfoInner").click()
