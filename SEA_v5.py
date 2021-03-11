#!/usr/bin/env python
# coding: utf-8

import re
import json
import os 
import pandas as pd
import flask
from flask import Flask
from flask import request
#for the search_text function
from difflib import get_close_matches 
from py_openthesaurus import OpenThesaurusWeb
open_thesaurus = OpenThesaurusWeb()
import logging
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


#Defining class for the rows (Accounts) in excel
class Account: #account_line
    def __init__(self, id, desc, searchTerms, negativeTerms, amount, duration, usage, stage2_logic, category,stage3_result):
        self.id = id
        self.desc = desc
        self.searchTerms = searchTerms
        self.negativeTerms = negativeTerms
        self.amount = amount
        self.duration = duration
        self.usage = usage
        self.stage2_logic = stage2_logic
        self.category = category
        self.stage3_result = stage3_result

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

#Defining class for the variables in excel
class Amount:
    def __init__(self, id):
        self.id = id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class Duration:
    def __init__(self, id):
        self.id = id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class Usage:
    def __init__(self, id):
        self.id = id


# Getting excel data into the predefined objects
def getExcelData():
    thisFolder = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(thisFolder, 'Datei.xlsx')
    excel_import = pd.read_excel(
        my_file, dtype=str)
    #excel_import = pd.read_excel(
    #    "C:\\Users\\cts\\Horváth & Partner GmbH\\IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx", dtype=str)
    listOfAccounts = []
    for index, row in excel_import.iterrows():
        searchTerms = [""] if pd.isnull(
            row.iloc[2]) else row.iloc[2].replace(" ", "").split(",")
        negativeTerms = [""] if pd.isnull(
            row.iloc[3]) else row.iloc[3].replace(" ", "").split(",")
        amount = Amount(re.split(",|\.", row.iloc[4]))
        duration = Duration(re.split(",|\.", row.iloc[5]))
        usage = Usage(row.iloc[6])
        stage2_logic=[""] if pd.isnull(
            row.iloc[8]) else row.iloc[8].replace(" ", "").split(",")
        listOfAccounts.append(
            Account(
                row.iloc[0],
                row.iloc[1],
                searchTerms,
                negativeTerms,
                amount,
                duration,
                usage,
                stage2_logic, # stage 2 logic id
                row.iloc[9], #übergeordnete kategories
                row.iloc[7] # stage3_result
            ))
    return listOfAccounts

#TODO fv-t magat bepakolni az account_list helyett?
account_list = getExcelData()

#Filtering for amount,duration, usage, categories
def amountSearch(results, amount):
    newResults = []
    for account in results:
        ids = account.amount.id
        for acc_amount in ids:
            if(str(acc_amount) == amount or str(acc_amount)=="0"):
                newResults.append(account)
    return newResults

def durationSearch(results, duration):
    newResults = []
    for account in results:
        ids = account.duration.id
        for acc_duration in ids:
            if(str(acc_duration) == duration):
                newResults.append(account)
    return newResults

def usageSearch(results, usage):
    newResults = []
    for account in results:
        if(str(account.usage.id) == usage): 
            newResults.append(account)
    return newResults

# TODO: above functions can be simplified by leaving out a for loop like this - using dictionaries instead-> faster!!!

def categorySearch(results, category):
    newResults = []
    for account in results:
        if(str(account.category) == category): 
            newResults.append(account)
    return newResults

### Stage 2: Amount, Duration, Usage question and answer dictionaries

#Question logic
def questionLogic(results):
    l_temp = []
    for account in results:
        l_temp.append(account.stage2_logic)
    if len(set([''.join(lst) for lst in l_temp]))==1: # converting list to string to be able to get the distinct list values
        newResults=l_temp[0]
    else:
        newResults=['Amount', 'Usage','Duration'] 
        # TODO:default question and order - beletenni hogy ha nincs usage a leszurt excelbe akk a default se legyen usage
    return newResults

#Importing additional excel sheets (id-text dictionaries) 
#amount
#xlsx = pd.ExcelFile('C:\\Users\\cts\\Horváth & Partner GmbH\\IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx')
thisFolder = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(thisFolder, 'Datei.xlsx')
xlsx = pd.ExcelFile(my_file)
#xlsx = pd.ExcelFile('C:\\Users\\hdo\\Horváth & Partner GmbH\HP SAP S4 ACCOUNT IDENTIFIER FEJLESZTES NP - IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx')
df = xlsx.parse(xlsx.sheet_names[1])
d_amount=df.set_index('ID').T.to_dict('records')[0]
#duration
df = xlsx.parse(xlsx.sheet_names[2])
d_duration=df.set_index('ID').T.to_dict('records')[0]
#usage
df = xlsx.parse(xlsx.sheet_names[3])
d_usage=df.set_index('ID').T.to_dict('records')[0]
#übergeordnete category
df = xlsx.parse(xlsx.sheet_names[4])
d_category=df.set_index('ID').T.to_dict('records')[0]

#Dictionary for übergeordnete categories 
d_cats={"id": "c1",
        "text": "Bitte wählen Sie eine Kategorie:",
        "answers": [
            {
                "id": "c1",
                "text": d_category["c1"]
            },
            {
                "id": "c2",
                "text": d_category["c2"]
            },
            {
                "id": "c3",
                "text": d_category["c3"]
            },
            {
                "id": "c4",
                "text": d_category["c4"]
            },
                        {
                "id": "c5",
                "text": d_category["c5"]
            },
                    {
                "id": "c6",
                "text": d_category["c6"]
            },
            {
                "id": "c7",
                "text": d_category["c7"]
            },
            {
                "id": "c8",
                "text": d_category["c8"]
            },
            {
                "id": "c9",
                "text": d_category["c9"]
            },
                        {
                "id": "c10",
                "text": d_category["c10"]
            },
                                    {
                "id": "c11",
                "text": d_category["c11"]
            },
            {
                "id": "c12",
                "text": d_category["c12"]
            }
        ],
        "infobox":None
}

#All potential answers to stage2 questions
#Answers for Amount and Duration questions
d_answers={1: {
              "id": 0,
              "text": "na",
              "question":"Amount"
              },
           2: {
              "id": 1,
              "text": "<10",
              "question":"Amount"
              },
           3: {
              "id": 2,
              "text": "10,01-59,99",
              "question":"Amount"
              },
           4: {
              "id": 3,
              "text": "60-249,99",
              "question":"Amount"
              },
           5: {
              "id": 4,
              "text": ">250",
              "question":"Amount"
              },
           6: {
              "id": 0,
              "text": "na",
              "question":"Duration"
              },
           7: {
              "id": 1,
              "text": "< 1 Jahr",
              "question":"Duration"
              },
           8: {
              "id": 2,
              "text": "> 1 Jahr",
              "question":"Duration"
              }
      }

#Adding answers for Usage questions to the d_answers dictionary
for i in range(1,len(d_usage)+1):
    d_answers[8+i]={
                "id": i,
                "text": d_usage[i],
                "question":"Usage"
                }
#d_answers id-s: 1 to 98

### Reversed dicts per question type to get the api_ids for the answers
#Amount
excel_ids=[]
for l in range(1,6):
    excel_ids.append(d_answers[l]["id"])
api_ids=[]
for l in range(1,6):
    api_ids.append(l)
d_amount_id=dict(zip(excel_ids,api_ids))
#Duration
excel_ids=[]
for l in range(6,9):
    excel_ids.append(d_answers[l]["id"])
api_ids=[]
for l in range(6,9):
    api_ids.append(l)
d_duration_id=dict(zip(excel_ids,api_ids))
#Usage
excel_ids=[]
for l in range(9,99):
    excel_ids.append(d_answers[l]["id"])
api_ids=[]
for l in range(9,99):
    api_ids.append(l)
d_usage_id=dict(zip(excel_ids,api_ids))

#Function for getting available answers for Amount,Duration,Usage quesstions
def create_answers(results):
    #Amount
    # list of available amount ids
    l_amount=[]
    for i in range(len(results)):
        l_amount.extend(results[i].amount.id)
    l_amount=list(set(l_amount))
    
    # if there is a 0 (na) then all the answers should be shown
    if "0" in l_amount:
        l_amount=["1","2","3","4"]
        
    #list of dictionaries of available amount ids
    l_answers_amount=[]
    for i in range(len(l_amount)): 
        s={
        "id": d_amount_id[int(l_amount[i])], #api id for l_amount[i]
        "text": d_amount[int(l_amount[i])] 
        }
        l_answers_amount.append(s)
        
    #Duration
    l_duration=[]
    for i in range(len(results)):
        l_duration.extend(results[i].duration.id)
    l_duration=list(set(l_duration))

    # if there is a 0 (na) then all the answers should be shown
    if "0" in l_duration:
        l_duration=["1","2"]

    l_answers_duration=[]
    for i in range(len(l_duration)): 
        s={
        "id": d_duration_id[int(l_duration[i])], 
        "text": d_duration[int(l_duration[i])] 
        }
        l_answers_duration.append(s)
        
    #Usage
    l_usage=[]
    for i in range(len(results)):
        l_usage.append(results[i].usage.id) #append instead of extend, because there are only 1 id there, with extend it doesnt work
    l_usage=list(set(l_usage))

    l_answers_usage=[]
    for i in range(len(l_usage)): 
        s={
        "id": d_usage_id[int(l_usage[i])], 
        "text": d_usage[int(l_usage[i])] 
        }
        l_answers_usage.append(s)

    #Getting rid of the nan answer for each question
    for i, d in enumerate(l_answers_duration):
        if pd.isna(d['text']):
            l_answers_duration.pop(i)
            break

    for i, d in enumerate(l_answers_amount):
        if pd.isna(d['text']):
            l_answers_amount.pop(i)
            break

    for i, d in enumerate(l_answers_usage):
        if pd.isna(d['text']):
            l_answers_usage.pop(i)
            break
    
    # ordering answer dictionaries:
        l_answers_amount=sorted(l_answers_amount, key = lambda i: i['id'])
        l_answers_duration=sorted(l_answers_duration, key = lambda i: i['id'])
        l_answers_usage=sorted(l_answers_usage, key = lambda i: i['id'])
    
    # d_questions dictionary with the questions and the potential answers
    d_questions={
    "Amount": {
        "id": 1,
        "text": "Betrag:",
        "answers": l_answers_amount,
        "infobox":"Bitte Betrag in NETTO EUR pro Einheit (bspw. sonstige Betriebsaufw., Büromaterial) oder pro Person (bspw. bei Bewirtung, Geschenken) angeben. Die Beträge müssen sich auf Positionen in einer Banf, Bestellung oder Angebot beziehen; nicht der Rechnungsbetrag."
    },
    "Duration": {
        "id": 2,
        "text": "Nutzungsdauer:",
        "answers":l_answers_duration,
        "infobox":"Geben Sie an, über welchen Zeitraum Sie Ihren gewünschten Bedarf voraussichtlich nutzen und er dem Unternehmen zur Verfügung steht."
    },
    "Usage": {
        "id": 3,
        "text": "Verwendungszweck:",
        "answers": l_answers_usage,
        "infobox":"Wählen Sie für Ihren Bedarf den dazu passenden Verwendungszweck aus. Bsp.:  Bedarf: 'Verschenken von Modellauto' -> Verwendungszweck: 'Empfänger: Mitarbeiter (für Bewirtung & Geschenke)'"
    }
    }
    return d_questions

### Stage 3 - Instandhaltung: linked lists for decision trees

#Defining Question and Answer class for the decision trees
class Question:
    def __init__(self, id, text, answers, infobox):
        self.id = id
        self.text =text
        self.answers = answers
        self.infobox = infobox

class Answer:
    def __init__(self, id, text, next_question,question,account_name): # account is egy plusz objektum
        self.id = id
        self.text = text
        self.next_question = next_question
        self.question=question
        self.account_name = account_name

#Question objects
#When beside Amount, Duration, Usage more questions or answers are used, these id-s should be changed as well
#Instandhaltung decision tree
q1=Question(4,"Handelt es sich um eine reine Instandhaltungsmaßnahme?",[{"id":101,"text":"Ja"},{"id":102,"text":"Nein"}], "Die Instandhaltung ist die Gesamtheit der Maßnahmen zur Bewahrung des Soll-Zustandes sowie zur Festlegung und Beurteilung des Ist-Zustandes. Solche Maßnahmen sind: (1) Inspektion (Feststellung und Beurteilung des Ist-Zustandes), (2) Wartung / Reparatur (Bewahrung des Soll-Zustandes), (3) Instandsetzung (Wiederherstellung des Soll-Zustandes).")
q2=Question(5,"Findet ein Austausch von bereits vorhandenen Gegenständen statt?",[{"id":103,"text":"Ja"},{"id":104,"text":"Nein"}], "Beispiele für den Austausch von bereits vorhandenen Gegenständen: (1) Austausch eines zerbrochenen Fensters am Firmengebäude, (2) Ölwechsel bei einem Kran, (3) Wartung einer Fertigungsmaschine, (4) Überwachung einer Produktionsanlage durch Messtechnik, (5) Reparatur der Sanitäranlagen im Firmengebäude")
q3=Question(6,"Wird durch die Maßnahme ein über dem einst vorhandenen Standard liegender Zustand erreicht (Standardhebung)?",[{"id":105,"text":"Ja"},{"id":106,"text":"Nein"}], "Indizien für die Standarderhebung: (1) ein Gebäude wird in zeitl. Nähe zum Erwerb im Ganzen und von Grund auf modernisiert, (2) hohe Aufw. für die Sanierung der zentralen Ausstattungsmerk. werden getätigt, (3) aufgrund dieser Baumaßnahme wird der Mietzins erheblich erhöht.")
#Werkvertrag/Dienstvertrag (WVDV) decision tree
q4=Question(7,"Handelt es sich um einen materiellen oder immateriellen Bedarf?",[{"id":107,"text":"Materiell"},{"id":108,"text":"Immateriell"}], "Materiell: Sache oder ein Gegenstand, der körperlich existiert (z.B. Gabelstapler, Schrauber). Immateriell: nicht körperlich greifbar (z.B. Dienstleistung, Lizenz)")
q5=Question(8,"Ist ein konkretes Arbeitsergebnis Gegenstand des Vertrags?",[{"id":109,"text":"Ja"},{"id":110,"text":"Nein"},{"id":111,"text":"Nicht bekannt"}],"Ein konkretes Arbeitsergebnis liegt vor, wenn die Verpflichtung zur Herstellung eines Werks / eines Ergebnisses (z.B. Reparaturvertrag, Erstellung von Gutachten) erfüllt ist.")
q6=Question(9,"Können alle Fragen in der Infobox bejaht werden?",[{"id":112,"text":"Ja"},{"id":113,"text":"Nein"}], "Das Unternehmen... (1) ...verfügt über fundiertes Know How (2) ...definiert Meilensteine (3) ...trägt/stellt die Projektverantwortung /-leiter (4) ...übernimmt Vorgaben und Überwachung (5) ...trägt die wesentlichen Chancen und Risiken (6) ...kann den Ausgang der Entwicklung beeinflussen (7) ...trägt das Produktrisiko")
#Sachgesamtheit / Aktivierung decision tree
q7=Question(10,"Gehört der Bedarf zu einer bestehenden / neuen Sachanlage? ",[{"id":114,"text":"Ja"},{"id":115,"text":"Nein"}], "Sachanlagen sind körperlich und greifbar (materiell), z.B. Laptop, Maschinen, Tisch")
q8=Question(11,"Ist die Anlagenummer bekannt?",[{"id":116,"text":"Ja"},{"id":117,"text":"Nein"}], "Geben Sie, falls der Bedarf zu einer bestehenden Anlage gehört, die entsprechende Anlagennummer an.")
q9=Question(12,"Handelt es sich bei Ihrem Bedarf um einen Gegenstand, der nicht selbstständig genutzt werden kann? (z.B. Dockingstation)",[{"id":118,"text":"Ja"},{"id":119,"text":"Nein"}], "Die selbständige Nutzung eines Gegenstandes setzt voraus, dass sie unabhängig von anderen Wirtschaftsgütern genutzt werden kann, bspw. Drucker.")
#Einkauf/Vertrieb decision tree
q10=Question(13,"Handelt es um Transportkosten mit Bezug auf den Vertrieb? (Ausgangsfracht)",[{"id":120,"text":"Ja"},{"id":121,"text":"Nein"}], "Zu den Transportkosten im Rahmen des Vertriebs gehören Waren, die an den Kunden ausgeliefert werden.")
q11=Question(14,"Handelt es sich um Versandkosten für ...?",[{"id":122,"text":"Fahrzeuge"},{"id":123,"text":"Ersatzteile"},{"id":124,"text":"Sonstiges"},{"id":125,"text":"Nein"}], None)
q12=Question(15,"Gehören die Transportkosten zu einer bestehenden / neuen Sachanlage?",[{"id":126,"text":"Ja"},{"id":127,"text":"Nein"}], "Sachanlagen sind körperlich und greifbar (materiell), z.B. Laptop, Maschinen, Tisch")
q13=Question(16,"Ist die Anlagenummer bekannt?",[{"id":128,"text":"Ja"},{"id":129,"text":"Nein"}], "Geben Sie, falls der Bedarf zu einer bestehenden Anlage gehört, die entsprechende Anlagennummer an.")
q14=Question(17,"Handelt es sich um Logistikkosten eines Serienlieferanten?)",[{"id":130,"text":"Ja"},{"id":131,"text":"Nein"}], "Zu den Serienlieferanten gehören bspw. Bosch und Mahle.")
q15=Question(18,"Weitere Spezifikation:",[{"id":132,"text":"Verpackung und Versand Material im Werk"},{"id":133,"text":"Eingangstransportkosten"},
                                         {"id":134,"text":"Ungeplante Bezugsnebenkosten"},{"id":135,"text":"Zölle"},
                                         {"id":136,"text":"See- / Frachtkosten"},{"id":137,"text":"Inboundkosten (WE, Verpackung, Einlagerung, Retouren) des Logistikdienstleisters PLOG"}], None)

#Answer objects
#When besoide Amount, Duration, Usage more questions or answers are used, these id-s should be changed as well
#Instandhaltung decision tree
a1=Answer(101,"Ja",next_question=q2,question=q1,account_name=None)
a2=Answer(102,"Nein",next_question=None,question=q1,account_name="Invest-Dummy-Konto")
a3=Answer(103,"Ja",next_question=q3,question=q2,account_name=None)
a4=Answer(104,"Nein",next_question=None,question=q2,account_name="Invest-Dummy-Konto")
a5=Answer(105,"Ja",next_question=None,question=q3,account_name="Invest-Dummy-Konto")
a6=Answer(106,"Nein",next_question=None,question=q3,account_name="Aufwandskonto")
#Werkvertrag/Dienstvertrag (WVDV) decision tree
a7=Answer(107,"Materiell",next_question=None,question=q4,account_name="Invest-Dummy-Konto")
a8=Answer(108,"Immateriell",next_question=q5,question=q4,account_name=None)
a9=Answer(109,"Ja",next_question=q6,question=q5,account_name=None)
a10=Answer(110,"Nein",next_question=None,question=q5,account_name="Aufwandskonto")
a11=Answer(111,"Nicht bekannt",next_question=None,question=q5,account_name="Invest-Dummy-Konto")
a12=Answer(112,"Ja",next_question=None,question=q6,account_name="Aufwandskonto")
a13=Answer(113,"Nein",next_question=None,question=q6,account_name="Invest-Dummy-Konto")
#Sachgesamtheit / Aktivierung decision tree
a14=Answer(114,"Ja",next_question=q8,question=q7,account_name=None)
a15=Answer(115,"Nein",next_question=q9,question=q7,account_name=None)
a16=Answer(116,"Ja",next_question=None,question=q8,account_name="Invest-Dummy-Konto")
a17=Answer(117,"Nein",next_question=None,question=q8,account_name="Invest-Dummy-Konto")
a18=Answer(118,"Ja",next_question=None,question=q9,account_name="Invest-Dummy-Konto")
a19=Answer(119,"Nein",next_question=None,question=q9,account_name="Aufwandskonto")
#Einkauf/Vertrieb decision tree
a20=Answer(120,"Ja",next_question=q11,question=q10,account_name=None)
a21=Answer(121,"Nein",next_question=q12,question=q10,account_name=None)
a22=Answer(122,"Fahrezeuge",next_question=None,question=q11,account_name="Specific account")
a23=Answer(123,"Ersatzteile",next_question=None,question=q11,account_name="Specific account")
a24=Answer(124,"Sonstiges",next_question=None,question=q11,account_name="Specific account")
a25=Answer(125,"Nein",next_question=None,question=q11,account_name="Specific account")
a26=Answer(126,"Ja",next_question=q13,question=q12,account_name=None)
a27=Answer(127,"Nein",next_question=q14,question=q12,account_name=None)
a28=Answer(128,"Ja",next_question=None,question=q13,account_name="Invest-Dummy-Konto")
a29=Answer(129,"Nein",next_question=None,question=q13,account_name="Invest-Dummy-Konto")
a30=Answer(130,"Ja",next_question=None,question=q14,account_name="Specific account")
a31=Answer(131,"Nein",next_question=q15,question=q14,account_name="Aufwandskonto")
a32=Answer(132,"Verpackung und Versand Material im Werk",next_question=None,question=q15,account_name="Specific account")
a33=Answer(133,"Eingangstransportkosten",next_question=None,question=q15,account_name="Specific account")
a34=Answer(134,"Ungeplante Bezugsnebenkosten",next_question=None,question=q15,account_name="Specific account")
a35=Answer(135,"Zölle",next_question=None,question=q15,account_name="Specific account")
a36=Answer(136,"See- / Frachtkosten",next_question=None,question=q15,account_name="Specific account")
a37=Answer(137,"Inboundkosten (WE, Verpackung, Einlagerung, Retouren) des Logistikdienstleisters PLOG",next_question=None,question=q15,account_name="Specific account")

#Decision tree dictionary
d_tree={ a1.id:a1,
         a2.id:a2,
         a3.id:a3,
         a4.id:a4,
         a5.id:a5,
         a6.id:a6,
         a7.id:a7,
         a8.id:a8,
         a9.id:a9,
         a10.id:a10,
         a11.id:a11,
         a12.id:a12,
         a13.id:a13,
         a14.id:a14,
         a15.id:a15,
         a16.id:a16,
         a17.id:a17,
         a18.id:a18,
         a19.id:a19,
         a20.id:a20,
         a21.id:a21,
         a22.id:a22,
         a23.id:a23,
         a24.id:a24,
         a25.id:a25,
         a26.id:a26,
         a27.id:a27,
         a28.id:a28,
         a29.id:a29,
         a30.id:a30,
         a31.id:a31,
         a32.id:a32,
         a33.id:a33,
         a34.id:a34,
         a35.id:a35,
         a36.id:a36,
         a37.id:a37
         }
#Search function with text search (synonyms, positive-negative keywords), categories, amount, duration, usage
def search_text(accounts, search_value, category=None, amount=None, duration=None, usage=None): 
    search_value_list = search_value.split(" ")
    results = []
    synonyms = []
 
    # searching for synonyms at open thesaurus
    for value in search_value_list:
        params = {"q":value, "format":"application/json"}
        r = requests.get('https://www.openthesaurus.de/synonyme/search', params=params)
        response = json.loads(r.text)
        synonyms_each = []
        for cat in response.get("synsets"):
            for synonym in cat.get("terms"):
                synonyms_each.append(synonym.get("term"))
        synonyms.extend(synonyms_each)
 
    for index, account in enumerate(accounts): # the index and enumerate stuff porbably just counts the loop numbers
        matches = 0
        negative_matches = 0
 
        # get_close_values is used to make the search case insensitive and more robust. With different cutoff values the closeness of the results can be set.
        for value in search_value_list: 
            if len(get_close_matches(value.casefold(), map(str.casefold, account.searchTerms), cutoff=0.8)) > 0: 
                matches += 1
        # if any synonym of the search term is in the list then we get a match
        for value in search_value_list:
            if any(item.casefold() in map(str.casefold, synonyms) for item in map(str.casefold, account.searchTerms)):
                matches += 1
 
        # if the searched term (robust search) or a synonym is in the negative keyword list then dont append to result
        for value in search_value_list: 
            if len(get_close_matches(value.casefold(), map(str.casefold, account.negativeTerms), cutoff=0.8)) > 0: 
                negative_matches += 1
        for value in search_value_list: 
            if any(item.casefold() in map(str.casefold, synonyms) in synonyms for item in map(str.casefold, account.negativeTerms)):
                negative_matches += 1
        
        #if at least one found word in keyword list and no negative matches then append to result!         
        if matches > 0 and negative_matches==0: 
            results.append(account)
        
    if(category != None):
        results = categorySearch(accounts, category) # when we have category, then we have to search from the given results and not from the text filtered accounts, becouse it is empty
    if(amount != None):
        results = amountSearch(results, amount) # using the predefined functions for amount, duration and usage search; only searching in the results that has been filtered above
    if(duration != None):
        results = durationSearch(results, duration) # only searching in the results that has been filtered above
    if(usage != None):
        results = usageSearch(results, usage) # only searching in the results that has been filtered above
    return results

# #Search function with text search (synonyms, positive-negative keywords), categories,amount,duration,usage
# def search_text(accounts, search_value, category=None, amount=None, duration=None, usage=None): 
#     search_value_list = search_value.split(" ")
#     results = []
#     synonyms = []

#     # searching for synonyms at open thesaurus
#     for value in search_value_list:
#             synonyms.extend(open_thesaurus.get_synonyms(value)) 

#     for index, account in enumerate(accounts): # the index and enumerate stuff porbably just counts the loop numbers
#         matches = 0
#         negative_matches = 0

#         # get_close_values is used to make the search case insensitive and more robust. With different cutoff values the closeness of the results can be set.
#         for value in search_value_list: 
#             if len(get_close_matches(value, account.searchTerms, cutoff=0.8)) > 0: 
#                 matches += 1
#         # if any synonym of the search term is in the list then we get a match
#         for value in search_value_list:
#             if any(item in synonyms for item in account.searchTerms): 
#                 matches += 1

#         # if the searched term (robust search) or a synonym is in the negative keyword list then dont append to result
#         for value in search_value_list: 
#             if len(get_close_matches(value, account.negativeTerms, cutoff=0.8)) > 0: 
#                 negative_matches += 1
#         for value in search_value_list: 
#             if any(item in synonyms for item in account.negativeTerms):
#                 negative_matches += 1
        
#         #if at least one found word in keyword list and no negative matches then append to result!         
#         if matches > 0 and negative_matches==0: 
#             results.append(account)
        
#     if(category != None):
#         results = categorySearch(accounts, category) # when we have category, then we have to search from the given results and not from the text filtered accounts, becouse it is empty
#     if(amount != None):
#         results = amountSearch(results, amount) # using the predefined functions for amount, duration and usage search; only searching in the results that has been filtered above
#     if(duration != None):
#         results = durationSearch(results, duration) # only searching in the results that has been filtered above
#     if(usage != None):
#         results = usageSearch(results, usage) # only searching in the results that has been filtered above
#     return results

# stage3 logic function for 1. post request
def stage3(results,content,filters):

    if results[0].stage3_result=="Account ID":
        dict2={ "sid":content["sid"],
        "result": {"text":results[0].desc,"id":results[0].id, "is_asset_number":False},
        "cat_list": None,
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)
        
    if results[0].stage3_result=="Dummy":
        dict2={ "sid":content["sid"],
        "result": {"text":"Invest-Dummy-Konto", "id":999910, "is_asset_number":False},
        "cat_list": None,
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)
        
    elif results[0].stage3_result=="Entscheidungsbaum (Instandhaltung)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "cat_list": None,
        "question": {
                    "id": q1.id,
                    "text": q1.text,
                    "answers": q1.answers,
                    "infobox":q1.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)  
    elif results[0].stage3_result=="Entscheidungsbaum (WVDV)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "cat_list": None,
        "question": {
                    "id": q4.id,
                    "text": q4.text,
                    "answers": q4.answers,
                    "infobox":q4.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 
    elif results[0].stage3_result=="Entscheidungsbaum (Sachgesamtheit)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "cat_list": None,
        "question": {
                    "id": q7.id,
                    "text": q7.text,
                    "answers": q7.answers,
                    "infobox":q7.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 

    elif results[0].stage3_result=="Entscheidungsbaum (Einkauf/Vertrieb)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "cat_list": None,
        "question": {
                    "id": q10.id,
                    "text": q10.text,
                    "answers": q10.answers,
                    "infobox":q10.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 
    return response

# stage3 logic function for 2. post request
def stage3_2(results,content,filters):

    if results[0].stage3_result=="Account ID":
        dict2={ "sid":content["sid"],
        "result": {"text":results[0].desc,"id":results[0].id, "is_asset_number":False},
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)
        
    elif results[0].stage3_result=="Dummy":
        dict2={ "sid":content["sid"],
        "result": {"text":"Invest-Dummy-Konto", "id":999910, "is_asset_number":False},
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)
        
    elif results[0].stage3_result=="Entscheidungsbaum (Instandhaltung)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "question": {
                    "id": q1.id,
                    "text": q1.text,
                    "answers": q1.answers,
                    "infobox":q1.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False)  
    elif results[0].stage3_result=="Entscheidungsbaum (WVDV)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "question": {
                    "id": q4.id,
                    "text": q4.text,
                    "answers": q4.answers,
                    "infobox":q4.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 
    elif results[0].stage3_result=="Entscheidungsbaum (Sachgesamtheit)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "question": {
                    "id": q7.id,
                    "text": q7.text,
                    "answers": q7.answers,
                    "infobox":q7.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 

    elif results[0].stage3_result=="Entscheidungsbaum (Einkauf/Vertrieb)":
        dict2={
        "sid": content["sid"],
        "result": None,
        "question": {
                    "id": q10.id,
                    "text": q10.text,
                    "answers": q10.answers,
                    "infobox":q10.infobox},
        "filter": filters
        }
        response=json.dumps(dict2, indent=4,ensure_ascii=False) 
    return response

@app.route('/api/search', methods=['POST'])

def search():
    """ Requires this request json: {"sid":"GUID","text":"user input"} """
    content = request.get_json()
    results=search_text(account_list,str(content['text'])) 
    filters={"search_text": content['text']}
    #3 options from here: 0 result, 1 result, several result
    if len(results)==0:
        dict1={ "sid":content["sid"],
                "result": None,
                "question": d_cats,
                "filter": filters
                }
        response=json.dumps(dict1, indent=4)
    elif len(results)==1:
        response=stage3(results,content,filters)
        
    elif len(results)>1:
        print(questionLogic(results))
        dict3={ "sid":content["sid"],
                "result": None,
                "question": create_answers(results)[questionLogic(results)[0]], # get the json of the first question from the d_question dict
                "filter": filters
                }
        response=json.dumps(dict3, indent=4,ensure_ascii=False)
    return response

@app.route('/api/questions', methods=['POST'])

def questions():
    """ Requires this request json: {
        "sid":"GUID",
        "answer_id": c3,
        "filter":{
            "search_text": "tasche",
            ...}} """ 
                     
    content = request.get_json()
    
    ##Checking what is already in the filter properties
    #category
    try: 
        Category=str({v: k for k, v in d_category.items()}[content["filter"]["Category"]]) # inverting dictionary, we need the id
    except: 
        Category=None
    #amount
    try: 
        Amount=str({v: k for k, v in d_amount.items()}[content["filter"]["Amount"]])
    except: 
        Amount=None
    #duration
    try: 
        Duration=str({v: k for k, v in d_duration.items()}[content["filter"]["Duration"]])
    except: 
        Duration=None
    #usage
    try: 
        Usage=str({v: k for k, v in d_usage.items()}[content["filter"]["Usage"]])
    except: 
        Usage=None
    
    
    #app.logger.info(str(content["filter"]))
    #app.logger.info(content["filter"]["Amount"])
    
    # Search function, parameters coming from the filter property
    results=search_text(account_list,str(content["filter"]["search_text"]),category=Category,amount=Amount,duration=Duration,usage=Usage)

    #Übergeordnete categories branch
    if content["answer_id"] in ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12']:
        results=categorySearch(account_list,str(content["answer_id"]))
        dict1={
        "sid": content["sid"],
        "result": None,
        "question": create_answers(results)[questionLogic(results)[0]],
        "filter": {
        "search_text": content["filter"]["search_text"],
        "Category": d_category[content["answer_id"]] 
        }
        }    
        response=json.dumps(dict1, indent=4,ensure_ascii=False)

    #stage2 logic
    elif content["answer_id"] != None and int(content["answer_id"])<=98: 

        str_question=d_answers[int(content["answer_id"])]["question"] #to which question I have the answer
        l_question_logic=questionLogic(results) # question order
        question_nr=l_question_logic.index(str_question) #  the index of the question that I have the answer
        #print(str_question)  
        #print(str(d_answers[int(content["answer_id"])]["id"]))         
        #filtering based on the answer, it is not in the search_text function, because it only works with the filter property
        if str_question == "Amount":
            results = amountSearch(results, str(d_answers[int(content["answer_id"])]["id"])) 
        elif (str_question == "Duration") : 
            results = durationSearch(results, str(d_answers[int(content["answer_id"])]["id"]))
        elif str_question == "Usage":
            results = usageSearch(results, str(d_answers[int(content["answer_id"])]["id"]))  
        
        #print(len(results))
        #print(results)
        
        #print(l_question_logic)
        
        #print(question_nr)

        #Adding to the existing filter, the new question-answer pair
        filters=str(content["filter"]).strip("}")+",'"+str(str_question)+"':'"+str(d_answers[int(content["answer_id"])]["text"])+"'}"
        filters=filters.replace("'","\"")
        filtero=json.loads(filters)

        # if there is 1 result-> stage3 logic
        if len(results)==1: 
            response=stage3_2(results,content,filtero)
        
        elif len(results)>1: # if there is >1 results
            #if the next question is null or we already asked the 3 questions, then decision tree
            if question_nr==3 or l_question_logic[question_nr+1]=="Null":
                response="After usage question, there will be only one result, this branch shouldnt exist"
                
            else:
                next_question=create_answers(results)[l_question_logic[question_nr+1]] # next question 
                #print(next_question)
                #print(l_question_logic[question_nr+1])
                dict3={
                        "sid": content["sid"],
                        "result": None,
                        "question": next_question,
                        "filter": filtero
                        }
                response=json.dumps(dict3, indent=4,ensure_ascii=False)
        elif len(results)<1:    
            response="Error: 0 in results!"

    elif int(content["answer_id"])>100: #Decision tree
    
        filters2=str(content["filter"]).strip("}")+",'"+d_tree[int(content["answer_id"])].question.text+"':'"+str(d_tree[int(content["answer_id"])].text)+"'}"
        filters2=filters2.replace("'","\"")
        filtero2=json.loads(filters2)
        if d_tree[int(content["answer_id"])].next_question is not None:
            dict4={
                    "sid": content["sid"],
                    "result": None,
                    "question": {
                                "id": d_tree[int(content["answer_id"])].next_question.id,
                                "text": d_tree[int(content["answer_id"])].next_question.text,                            
                                "answers": d_tree[int(content["answer_id"])].next_question.answers,
                                "infobox": d_tree[int(content["answer_id"])].next_question.infobox},
                    "filter": filtero2
                    }
            response=json.dumps(dict4, indent=4,ensure_ascii=False)
        else:
            if d_tree[int(content["answer_id"])].account_name=="Invest-Dummy-Konto":
                #there are 2 Asset number questions, when the Account is Invest-Dummy-Konto
                if d_tree[int(content["answer_id"])].id in [128,116]:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":d_tree[int(content["answer_id"])].account_name, "id":999910, "is_asset_number":True}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                else:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":d_tree[int(content["answer_id"])].account_name, "id":999910, "is_asset_number":False}, #id of Invest-dummy-Konto
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                
            elif d_tree[int(content["answer_id"])].account_name=="Specific account":
                if d_tree[int(content["answer_id"])].id==122:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Versandkosten Fahrzeuge", "id":691000, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==123:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Versandkosten Ersatzteile", "id":691100, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==124:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Versandkosten sonstige", "id":691200, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==125:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Kundenkulanz Sonderthemen", "id":691210, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==130:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Verpackungskosten der Lieferanten", "id":604400, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==132:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Verpackung und Versand Material im Werk", "id":604000, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==133:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Eingangstransportkosten", "id":691300, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==134:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Ungeplante Bezugsnebenkosten", "id":691310, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==135:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Zölle", "id":691350, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==136:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"See- / Frachtkosten", "id":6604300, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
                elif d_tree[int(content["answer_id"])].id==137:
                    dict5={
                            "sid": content["sid"],
                            "result": {"text":"Inboundkosten (WE, Verpackung, Einlagerung, Retouren) des Logistikdienstleisters PLOG", "id":604310, "is_asset_number":False}, 
                            "question": None,
                            "filter": filtero2
                            }
                    response=json.dumps(dict5, indent=4,ensure_ascii=False)
            else: # this branch is Aufwandskonto
                dict5={
                "sid": content["sid"],
                "result": {"text":results[0].desc,"id":results[0].id, "is_asset_number":False},
                "question": None,
                "filter": filtero2
                }
                response=json.dumps(dict5, indent=4,ensure_ascii=False)

    return response

@app.route('/api/asset', methods=['POST'])

def asset():
    """ Requires this request json: {
        "sid":"GUID",
        "text": "123456",
        "filter":{
            "search_text": "tasche",
            ...}} """ 
    
    #content = request.get_json()
    response = flask.Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

#TODO: 
# a questionLogic fv-ben a defaultba ne legyen olyan, amit nem lehet kérdezni! meg kell nézni, hogy milyen question logicok vannak és ami abba van, azt jelenítsae csak meg.
# lementés egy táblába, 

#komment



