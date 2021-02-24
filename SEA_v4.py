#!/usr/bin/env python
# coding: utf-8

import re
import json
import pandas as pd
from flask import Flask
from flask import request
#for the search_text function
from difflib import get_close_matches 
from py_openthesaurus import OpenThesaurusWeb
open_thesaurus = OpenThesaurusWeb()

app = Flask(__name__)

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

def getExcelData():
    #thisFolder = os.path.dirname(os.path.abspath(__file__))
    #my_file = os.path.join(thisFolder, 'Datei.xlsx')
    #excel_import = pd.read_excel(
    #    my_file, dtype=str)
    excel_import = pd.read_excel(
        "C:\\Users\\cts\\Horváth & Partner GmbH\\IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx", dtype=str)
    #excel_import = pd.read_excel(
        #"C:\\Users\\hdo\\Horváth & Partner GmbH\HP SAP S4 ACCOUNT IDENTIFIER FEJLESZTES NP - IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx", dtype=str)
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

account_list = getExcelData()

def amountSearch(results, amount):
    newResults = []
    for account in results:
        ids = account.amount.id
        for acc_amount in ids:
            if(str(acc_amount) == amount):
                newResults.append(account)
    return newResults

def durationSearch(results, duration):
    newResults = []
    for account in results:
        ids = account.duration.id
        for id in ids:
            if(str(id) == duration):
                newResults.append(account)
    return newResults


def usageSearch(results, usage):
    newResults = []
    for account in results:
        if(str(account.usage.id) == usage): # above functions can be simplified by leaving out a for loop like this - using dictionaries instead-> faster!!!
            newResults.append(account)
    return newResults

#Filtering for categories
def categorySearch(results, category):
    newResults = []
    for account in results:
        if(str(account.category) == category): 
            newResults.append(account)
    return newResults

#Question logic
def questionLogic(results):
    l_temp = []
    for account in results:
        l_temp.append(account.stage2_logic)
    if len(set([''.join(lst) for lst in l_temp]))==1: # converting list to string to be able to get the distinct list values
        newResults=l_temp[0]
    else:
        newResults=['Amount', 'Duration', 'Usage'] # default question and order - beletenni hogy ha nincs usage a leszurt excelbe akk a default se legyenusage
    return newResults


#Dictionary import (#https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary)
#amount
xlsx = pd.ExcelFile('C:\\Users\\cts\\Horváth & Partner GmbH\\IFUA-IDEX.TAN.T55170 - 02_Munka\\01_Projektmunka_IFUA\\Datei.xlsx')
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
for i in range(1,len(d_usage)):
    d_answers[8+i]={
                "id": i,
                "text": d_usage[i],
                "question":"Usage"
                }
#d_answers id-s: 1 to 98


### Stage 2: Amount, Duration, Usage question and answer dictionaries

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
for l in range(9,98):
    excel_ids.append(d_answers[l]["id"])
api_ids=[]
for l in range(9,98):
    api_ids.append(l)
d_usage_id=dict(zip(excel_ids,api_ids))


#Function for creating available answers for Amount,Duration,Usage quesstions
def create_answers(results):
    #Amount
    l_amount=[]
    for i in range(len(results)):
        l_amount.extend(results[i].amount.id)
    l_amount=list(set(l_amount))

    l_answers_amount=[]
    for i in range(len(l_amount)): 
        s={
        "id": d_amount_id[int(l_amount[i])], #l_amount[i]-hez a megfelelő api id kell
        "text": d_amount[int(l_amount[i])] 
        }
        l_answers_amount.append(s)
    #Duration
    l_duration=[]
    for i in range(len(results)):
        l_duration.extend(results[i].duration.id)
    l_duration=list(set(l_duration))

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
        
    d_questions={
    "Amount": {
        "question": {
        "id": 1,
        "text": "Amount?"
        },
        "answers": l_answers_amount
    },
    "Duration": {
        "question": {
        "id": 2,
        "text": "Duration?"
        },
        "answers":l_answers_duration
    },
    "Usage": {
        "question": {
        "id": 3,
        "text": "Usage?"
        },
        "answers": l_answers_usage
    }
    }
    return d_questions


### Stage 3 - Instandhaltung: linked lists for decision trees

#Question és Answer class inicializálása
class Question:
    def __init__(self, id, text, answers):
        self.id = id
        self.text =text
        self.answers = answers

class Answer:
    def __init__(self, id, text, next_question,question,account_name): # account is egy plusz objektum
        self.id = id
        self.text = text
        self.next_question = next_question
        self.question=question
        self.account_name = account_name


#Question objects
#When besoide Amount, Duration, Usage more questions or answers are used, these id-s should be changed as well
#Instandhaltung decision tree
q1=Question(4,"Handelt es sich um eine reine Instandhaltungsmaßnahme?",[{"id":101,"text":"Ja"},{"id":102,"text":"Nein"}])
q2=Question(5,"Findet ein Austausch von bereits vorhandenen Gegenständen statt?",[{"id":103,"text":"Ja"},{"id":104,"text":"Nein"}])
q3=Question(6,"Wird durch die Maßnahme ein über dem einst vorhandenen Standard liegender Zustand erreicht (Standardhebung)?",[{"id":105,"text":"Ja"},{"id":106,"text":"Nein"}])
#Werkvertrag/Dienstvertrag (WVDV) decision tree
q4=Question(7,"Handelt es sich um einen materiellen oder immateriellen Bedarf?",[{"id":107,"text":"Materiell"},{"id":108,"text":"Immateriell"}])
q5=Question(8,"Ist ein konkretes Arbeitsergebnis Gegenstand des Vertrags?",[{"id":109,"text":"Ja"},{"id":110,"text":"Nein"},{"id":111,"text":"Nicht bekannt"}])
q6=Question(9,"Können alle Fragen in der grauen Box (Z. D14) bejaht werden? (Hersteller)",[{"id":112,"text":"Ja"},{"id":113,"text":"Nein"}])
#Sachgesamtheit / Aktivierung decision tree
q7=Question(10,"Gehört der Bedarf zu einer bestehenden / neuen Sachanlage? ",[{"id":114,"text":"Ja"},{"id":115,"text":"Nein"}])
q8=Question(11,"Bitte geben Sie die Anlagennummer an.",[{"id":116,"text":"Bitte angeben"},{"id":117,"text":"Unbekannt"}])
q9=Question(12,"Handelt es sich bei Ihrem Bedarf um einen Gegenstand, der nicht selbstständig genutzt werden kann? (z.B. Dockingstation)",[{"id":118,"text":"Ja"},{"id":119,"text":"Nein"}])
#Einkauf/Vertrieb decision tree
#q10=Question(13,"Handelt es um Transportkosten mit Bezug auf den Vertrieb? (Ausgangsfracht)",[{"id":120,"text":"Ja"},{"id":121,"text":"Nein"}])
#q11=Question(14,"Handelt es sich um Versandkosten für ...?",[{"id":114,"text":"Fahrzeuge"},{"id":114,"text":"Fahrzeuge"},{"id":114,"text":"Fahrzeuge"},.........{"id":115,"text":"Nein"}])

#it doesnt make sense. decision trees should only be used to decide if invest dummy konto or aufwandskonto should be used


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
a16=Answer(116,"Bitte angeben",next_question=None,question=q8,account_name="Invest-Dummy-Konto")
a17=Answer(117,"Unbekannt",next_question=None,question=q8,account_name="Invest-Dummy-Konto")
a18=Answer(118,"Ja",next_question=None,question=q9,account_name="Invest-Dummy-Konto")
a19=Answer(119,"Nein",next_question=None,question=q9,account_name="Aufwandskonto")
#Einkauf/Vertrieb decision tree

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
         a19.id:a19
         }


#Übergeordnete kategorie 
d_cats={
        "question": {
            "id": "c1",
            "text": "Please choose a category:"
        },
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
            }
        ]
}


def search_text(accounts, search_value, category=None, amount=None, duration=None, usage=None): 
    search_value_list = search_value.split(" ") # adjusted the code based on the Nonetype error - now it works
    results = []
    synonyms = []

    # searching for synonyms at open thesaurus
    for value in search_value_list:
            synonyms.extend(open_thesaurus.get_synonyms(value)) 

    for index, account in enumerate(accounts): # the index and enumerate stuff porbably just counts the loop numbers
        matches = 0
        negative_matches = 0

        # get_close_values is used to make the search case insensitive and more robust. With different cutoff values the closeness of           the results can be set.
        for value in search_value_list: 
            if len(get_close_matches(value, account.searchTerms, cutoff=0.8)) > 0: 
                matches += 1
        # if any synonym of the search term is in the list then we get a match
        for value in search_value_list:
            if any(item in synonyms for item in account.searchTerms): 
                matches += 1

        # if the searched term (robust search) or a synonym is in the negative keyword list then dont append to result
        for value in search_value_list: 
            if len(get_close_matches(value, account.negativeTerms, cutoff=0.8)) > 0: 
                negative_matches += 1
        for value in search_value_list: 
            if any(item in synonyms for item in account.negativeTerms):
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

search_text(accounts=account_list, search_value="stanitzel rotten")[0].desc

# function for 1. post request
def stage3(results,content,filters):
    #stage3
    if results[0].stage3_result=="Account ID":
        dict2={ "sid":content["sid"],
        "result_acc": {"name":results[0].desc,"id":results[0].id},
        "cat_list": None,
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4)
    elif results[0].stage3_result=="Entscheidungsbaum (Instandhaltung)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "cat_list": None,
        "question": {
                    "id": q1.id,
                    "text": q1.text
                    },
                    "answers": q1.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4)  
    elif results[0].stage3_result=="Entscheidungsbaum (WVDV)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "cat_list": None,
        "question": {
                    "id": q4.id,
                    "text": q4.text
                    },
                    "answers": q4.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4) 
    elif results[0].stage3_result=="Entscheidungsbaum (Sachgesamtheit)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "cat_list": None,
        "question": {
                    "id": q7.id,
                    "text": q7.text
                    },
                    "answers": q7.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4) 

    elif results[0].stage3_result=="Entscheidungsbaum (Einkauf/Vertrieb)":
        response="Entscheidungsbaum (Einkauf/Vertrieb) - have to clear the logic"
    return response

# function for 2. post request
def stage3_2(results,content,filters):
    #stage3
    if results[0].stage3_result=="Account ID":
        dict2={ "sid":content["sid"],
        "result_acc": {"name":results[0].desc,"id":results[0].id},
        "question": None,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4)
    elif results[0].stage3_result=="Entscheidungsbaum (Instandhaltung)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "question": {
                    "id": q1.id,
                    "text": q1.text
                    },
                    "answers": q1.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4)  
    elif results[0].stage3_result=="Entscheidungsbaum (WVDV)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "question": {
                    "id": q4.id,
                    "text": q4.text
                    },
                    "answers": q4.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4) 
    elif results[0].stage3_result=="Entscheidungsbaum (Sachgesamtheit)":
        dict2={
        "sid": content["sid"],
        "result_acc": None,
        "question": {
                    "id": q7.id,
                    "text": q7.text
                    },
                    "answers": q7.answers,
        "filter": filters
        }
        response=json.dumps(dict2, indent=4) 

    elif results[0].stage3_result=="Entscheidungsbaum (Einkauf/Vertrieb)":
        response="Entscheidungsbaum (Einkauf/Vertrieb) - have to clear the logic"
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
                "result_acc": None,
                "question": d_cats,
                "filter": filters
                }
        response=json.dumps(dict1, indent=4)
    elif len(results)==1:
        response=stage3(results,content,filters)
        
    elif len(results)>1:

        dict3={ "sid":content["sid"],
                "result_acc": None,
                "question": create_answers(results)[questionLogic(results)[0]], # get the json of the first question from the d_question dict
                "filter": filters
                }
        response=json.dumps(dict3, indent=4)
    return response


#if __name__ == "__main__":
#    app.run(host='127.0.0.1', port=5000)


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
        Category=str({v: k for k, v in d_category.items()}[content["filter"]["Category"]]) # inverting dictionary, az id-ja kell
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

    results=search_text(account_list,str(content["filter"]["search_text"]),category=Category,amount=Amount,duration=Duration,usage=Usage)

    if content["answer_id"] in ["c1","c2","c3","c4","c5"]: #TODO make it dynamic
        results=categorySearch(account_list,str(content["answer_id"]))
        dict1={
        "sid": content["sid"],
        "result_acc": None,
        "question": create_answers(results)[questionLogic(results)[0]], # get the json of the first question from the d_question dict
        "filter": {
        "search_text": content["filter"]["search_text"],
        "Category": d_category[content["answer_id"]] 
        }
        }    
        response=json.dumps(dict1, indent=4)

    elif content["answer_id"] != None and int(content["answer_id"])<=98: 

        str_question=d_answers[content["answer_id"]]["question"]# melyik kérdésre kaptam választ
                   
        #szűrés az érkezett válaszra - ez nincs benne a fenti search_text fv-ben, ott csak azok legyenek amik már a filter propertieben szerepelnek
        if str_question == "Amount":
            results = amountSearch(results, str(d_answers[content["answer_id"]]["id"])) 
        elif (str_question == "Duration") : 
            results = durationSearch(results, str(d_answers[content["answer_id"]]["id"]))
        elif str_question == "Usage":
            results = usageSearch(results, str(d_answers[content["answer_id"]]["id"]))  

        l_question_logic=questionLogic(results) # kérdéssorrend
        question_nr=l_question_logic.index(str_question) #  amelyik kérdésre a választ kaptam annak mi az indexe

        #Adding to the existing filter, the new question-answer pair - TODO: work on nicer formating - encoding!!
        filters=str(content["filter"]).strip("}")+",'"+str(str_question)+"':'"+str(d_answers[content["answer_id"]]["text"])+"'}"

        # ha 1 results van, ha több results van
        if len(results)==1: # if there is 1 result->stage3
            
            response=stage3_2(results,content,filters)
        
        elif len(results)>1:
            #ha null a kövi kérdés vagy megvolt a 3 kérdés, akkor itt ugrik át a decision tree-re
            if question_nr==3 or l_question_logic[question_nr+1]=="Null":

                print("After usage question, there will be only one result, this branch shouldnt exist")

                response="After usage question, there will be only one result, this branch shouldnt exist"
            else:
                next_question=create_answers(results)[l_question_logic[question_nr+1]] # next question 

                dict3={
                        "sid": content["sid"],
                        "result_acc": None,
                        "question": next_question,
                        "filter": filters
                        }
                response=json.dumps(dict3, indent=4)
        elif len(results)<1:    
            response="Error: 0 in results!"

    elif content["answer_id"]>100: #Decision tree

        filters2=str(content["filter"]).strip("}")+",'"+d_tree[content["answer_id"]].question.text+"':'"+str(d_tree[content["answer_id"]].text)+"'}"

        if d_tree[content["answer_id"]].next_question is not None:
            dict4={
                    "sid": content["sid"],
                    "result_acc": None,
                    "question": {
                                "id": d_tree[content["answer_id"]].next_question.id,
                                "text": d_tree[content["answer_id"]].next_question.text
                                },
                                "answers": d_tree[content["answer_id"]].next_question.answers,
                    "filter": filters2
                    }
            response=json.dumps(dict4, indent=4)
        else:
            if d_tree[content["answer_id"]].account_name=="Invest-Dummy-Konto":
                dict5={
                        "sid": content["sid"],
                        "result_acc": {"name":d_tree[content["answer_id"]].account_name, "id":999910}, #id of Invest-dummy-Konto
                        "question": None,
                        "filter": filters2
                        }
                response=json.dumps(dict5, indent=4)
            else: # this branch is Aufwandskonto
                dict5={
                "sid": content["sid"],
                "result_acc": {"name":results[0].desc,"id":results[0].id},
                "question": None,
                "filter": filters2
                }
                response=json.dumps(dict5, indent=4)

    return response
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)


#TODO: 
# a questionLogic fv-ben a defaultba ne legyen olyan, amit nem lehet kérdezni! meg kell nézni, hogy milyen question logicok vannak és ami abba van, azt jelenítsae csak meg.
# lementés egy táblába, 
# json kiírás utf8 kódolásba-> Taschenrechner keresésre szétesik a szöveg





