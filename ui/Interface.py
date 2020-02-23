from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import requests
import lxml.html
import os
from selenium.webdriver.common.keys import Keys
import time
import webbrowser
import re
from selenium.webdriver.common.action_chains import ActionChains

from utils.Calcul import *
from tkinter import *


class Interface(Frame):

    def __init__(self, fenetre, **kwargs):

        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.pack(fill=BOTH)

        global liste
        liste = Listbox(fenetre)
        liste.pack()

        liste.insert(END, "Ligue 1")
        liste.insert(END, "Ligue 2")
        liste.insert(END, "Premier League")
        self.bouton_odds = Button(self, text="Get odds", command=self.championshipChoice)
        self.bouton_odds.pack()

    def getBook(self, id):
        print(id)
        beginClass = 'book-icon book-icon-b'

        if (beginClass + '24') == id:
            return 'Betclic'
        elif (beginClass + '21') == id:
            return 'PMU'
        elif (beginClass + '20') == id:
            return 'Unibet'
        elif (beginClass + '22') == id:
            return 'Parions Sport'
        elif (beginClass + '33') == id:
            return 'Winamax'
        elif (beginClass + '34') == id:
            return 'Zebet'
        elif (beginClass + '36') == id:
            return 'Betstars'
        else:
            return 'Book de merde'

    def correctTeamNames(self, equipe):
        if equipe == 'Estac Troyes':
            equipe = 'Troyes'

        if equipe == 'Rodez Aveyron':
            equipe = 'Rodez'

        if equipe == 'Clermont Foot':
            equipe = 'Clermont'

        if equipe == 'Toulouse Fc':
            equipe = 'Toulouse'

        if equipe == 'St. Etienne':
            equipe = 'St Etienne'

        if equipe == 'Sc Amiens':
            equipe = 'Amiens'

        if equipe == 'Psg':
            equipe = 'Paris SG'

        if equipe == 'AC Ajaccio':
            equipe = 'Ajaccio'

        return equipe;

    def championshipChoice(self):
        value = liste.get(liste.curselection()).replace(' ', '-').lower()
        self.getOdds(value)

    def getOdds(self, championship):
        ODDSPORTAL = 'https://www.oddsportal.com/soccer/france/' + championship + '/'
        print(ODDSPORTAL)
        COTEUR = 'https://www.coteur.com/cotes/france-' + championship + '-cid4.html'
        # ODDSPORTAL = 'https://www.oddsportal.com/soccer/france/ligue-1/'
        # COTEUR = 'https://www.coteur.com/cotes/france-ligue-1-cid3.html'

       # timestr = time.strftime("%d%m%Y-%H%M")
        timestr = time.strftime("%d%m%Y")
        filename = "output/"+ championship + "-" + timestr + ".txt"
        # filename = "LIGUE1-"+timestr+".txt"

        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("Can not delete the file as it doesn't exists")

        cotes = []
        cotes1XBET = {}

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument('log-level=3')
        driver = webdriver.Chrome('chromedriver', chrome_options=options)

        # RECUPERATION DES COTES SUR ODDSPORTAL.COM

        driver.get(ODDSPORTAL)

        compteur = 0
        elements = driver.find_elements_by_class_name('table-participant')
        count = len(elements) if len(elements) < 11 else 10

        while compteur < count:

            element = elements[compteur]
            url = element.find_element_by_xpath(".//a[not(contains(@href,'void'))]").get_attribute('href')
            print(url)

            body = driver.find_element_by_tag_name("body")
            body.send_keys(Keys.CONTROL + 't')
            driver.get(url)
            opposants = driver.find_element_by_tag_name('h1').text
            equipe1 = opposants.split(' - ')[0]
            equipe2 = opposants.split(' - ')[1]
            element2 = driver.find_elements_by_class_name('table-main')[0]

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "odd")))

            ligne = element2.find_element_by_xpath(
                ".//a[contains(text(),'1xBet')]/ancestor::tr").find_elements_by_class_name('odds')

            cote_equipe1 = ligne[0].find_element_by_xpath(".//div[1]").text
            cote_X = ligne[1].find_element_by_xpath(".//div[1]").text
            cote_equipe2 = ligne[2].find_element_by_xpath(".//div[1]").text

            if compteur == 0:
                cotes.append(equipe1 + " " + cote_equipe1 + " - " + cote_X + " - " + cote_equipe2 + " " + equipe2)
                equipe1 = equipe1.lower().replace(" ", "_")
                equipe2 = equipe2.lower().replace(" ", "_")
                cotes1XBET[equipe1] = cote_equipe1
                cotes1XBET[equipe1 + 'X'] = cote_X
                cotes1XBET[equipe2] = cote_equipe2



            elif compteur > 1:
                cotes.append(equipe1 + " " + cote_equipe1 + " - " + cote_X + " - " + cote_equipe2 + " " + equipe2)

                equipe1 = equipe1.lower().replace(" ", "_")
                equipe2 = equipe2.lower().replace(" ", "_")
                cotes1XBET[equipe1] = cote_equipe1
                cotes1XBET[equipe1 + 'X'] = cote_X
                cotes1XBET[equipe2] = cote_equipe2

            compteur = compteur + 1
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')

        print(cotes1XBET)
        cotes = sorted(cotes)

        '''

        file = open(filename,"a",encoding='utf-8')
        file.write("---COTES 1XBET---\n")
        for cote in cotes:
            file.write(cote+"\n")
        file.write("\n")

        file.close()

        '''

        # RECUPERATION DES COTES SUR COTEUR.COM

        cotes = []
        driver.get(COTEUR)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "odds")))

        tableauARJEL = driver.find_elements_by_xpath("//table[contains(@id,'mediaTable')]")[0]
        ligne = tableauARJEL.find_elements_by_xpath(".//tr[starts-with(@id,'renc')]")

        # driver.execute_script("window.scrollTo(0, 400)")

        i = 0

        for rencontre in ligne:

            opposants = rencontre.find_element_by_xpath(".//td[3]").text
            equipe1 = opposants.split(' - ')[0]
            equipe2 = opposants.split(' - ')[1]

            equipe1 = self.correctTeamNames(equipe1)
            equipe2 = self.correctTeamNames(equipe2)

            button_equipe1 = rencontre.find_element_by_xpath(".//td[6]/button[1]")
            cote_equipe1 = button_equipe1.text

            button_X = rencontre.find_element_by_xpath(".//td[7]/button[1]")
            cote_X = button_X.text

            button_equipe2 = rencontre.find_element_by_xpath(".//td[8]/button[1]")
            cote_equipe2 = button_equipe2.text

            equipe1_id = equipe1.lower().replace(" ", "_")
            equipe2_id = equipe2.lower().replace(" ", "_")
            print(equipe1 + equipe1_id)
            nom_books_equipe1 = ""
            nom_books_X = ""
            nom_books_equipe2 = ""

            if (cotes1XBET[equipe1_id] < cote_equipe1):
                meilleur_cote_1 = cote_equipe1
                print("cote ARJEL supérieure:" + equipe1)
                '''
                actions = ActionChains(driver)
                actions.move_to_element(button_equipe1).perform()
                '''

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, "//table[contains(@id,'mediaTable')]//tr[starts-with(@id,'renc')]//td[6]//button[1]")))
                time.sleep(1)

                button_equipe1.click()
                books = driver.find_elements_by_xpath("//b[contains(@class,'orange')]/preceding-sibling::a/span")
                for book in books:
                    id_book = book.get_attribute("class")
                    if nom_books_equipe1 == "":

                        nom_books_equipe1 += self.getBook(id_book)
                    else:
                        nom_books_equipe1 += "/" + self.getBook(id_book)

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger")))
                driver.find_element_by_class_name('btn-danger').click()


            else:
                meilleur_cote_1 = cotes1XBET[equipe1_id]
                print("cote 1XBET supérieure:" + equipe1)
                nom_books_equipe1 = "1XBET"

            if (cotes1XBET[equipe2_id] < cote_equipe2):
                meilleur_cote_2 = cote_equipe2
                print("cote ARJEL supérieure:" + equipe2)
                '''
                actions = ActionChains(driver)
                actions.move_to_element(button_equipe2).perform()
                driver.execute_script("arguments[0].scrollIntoView();", button_equipe2)
                '''

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, "//table[contains(@id,'mediaTable')]//tr[starts-with(@id,'renc')]//td[8]//button[1]")))
                time.sleep(1)
                button_equipe2.click()

                books = driver.find_elements_by_xpath("//b[contains(@class,'orange')]/preceding-sibling::a/span")
                for book in books:
                    id_book = book.get_attribute("class")
                    if nom_books_equipe2 == "":
                        nom_books_equipe2 += self.getBook(id_book)
                    else:
                        nom_books_equipe2 += "/" + self.getBook(id_book)

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger")))
                driver.find_element_by_class_name('btn-danger').click()

            else:
                meilleur_cote_2 = cotes1XBET[equipe2_id]
                print("cote 1XBET supérieure:" + equipe2)
                nom_books_equipe2 = "1XBET"

            if (cotes1XBET[equipe1_id + 'X'] < cote_X):
                meilleur_cote_X = cote_X

                '''
                actions = ActionChains(driver)
                actions.move_to_element(button_equipe2).perform()
                driver.execute_script("arguments[0].scrollIntoView();", button_equipe2)
                '''

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                    (By.XPATH, "//table[contains(@id,'mediaTable')]//tr[starts-with(@id,'renc')]//td[7]//button[1]")))
                time.sleep(1)
                button_X.click()

                books = driver.find_elements_by_xpath("//b[contains(@class,'orange')]/preceding-sibling::a/span")
                for book in books:
                    id_book = book.get_attribute("class")
                    if nom_books_X == "":
                        nom_books_X += self.getBook(id_book)
                    else:
                        nom_books_X += "/" + self.getBook(id_book)

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-danger")))
                driver.find_element_by_class_name('btn-danger').click()

            else:
                meilleur_cote_X = cotes1XBET[equipe1_id + 'X']
                print("cote 1XBET supérieure:" + equipe2)
                nom_books_X = "1XBET"

            i = i + 1

            trj = Calcul.calcul_trj(meilleur_cote_1,meilleur_cote_X,meilleur_cote_2)
            cotes.append(
                "(" + nom_books_equipe1 + ") " + equipe1 + " " + meilleur_cote_1 + " - " + meilleur_cote_X + "(" + nom_books_X + ") - " + meilleur_cote_2 + " " + equipe2 + " (" + nom_books_equipe2 + ") TRJ =" + trj)

        cotes = sorted(cotes)

        file = open(filename, "a", encoding='utf-8')
        file.write("---MEILLEURES COTES---\n\n\n")
        for cote in cotes:
            file.write(cote + "\n\n")
        file.write("\n")

        file.close()

        driver.close()
        driver.quit()
        #os.startfile(os.getcwd() +"\\output\\"+filename)
        #os.startfile("output/"+filename)
        #webbrowser.open(os.getcwd() + "/output/"+filename)
