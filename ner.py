from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

import os
java_path = "C:/Program Files/Java/jdk1.8.0_191/bin/java.exe"
os.environ['JAVAHOME'] = java_path

st = StanfordNERTagger('stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz',
                       'stanford-ner-2018-10-16/stanford-ner.jar',
                       encoding='utf-8')


text = """The House Oversight and Government Reform Committee plans to revive efforts in the new Congress to look into the White House's use of private emails amid reports that Ivanka Trump used her personal account through much of 2017 to trade messages with Cabinet officials, White House aides and other government employees.
The likely incoming Democratic chairman of the committee, Elijah Cummings of Maryland, plans to renew efforts to look into private emails next year after the Republican-controlled panel dropped its investigation into the matter when a separate controversy arose last year, according to a Cummings aide."""
text2 = "John walked through The Park"
tokenized_text = word_tokenize(text)
classified_text = st.tag(tokenized_text)

entities = []
last_class = "O"
word = ''
for i in range(len(classified_text)):
    current_class = classified_text[i][1]
    current_word = classified_text[i][0]
    if current_class != "O":
        word += current_word+"_"
    if last_class != "O" and not last_class == current_class:
        entities.append([word[:-1], last_class])
        word = ''
    #print(classified_text[i][0])
    last_class = current_class

from SPARQLWrapper import SPARQLWrapper, JSON
def getUrl(word):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = """
            PREFIX dbo:  <http://dbpedia.org/ontology/>
            PREFIX dbpedia: <http://dbpedia.org/resource/>
            SELECT DISTINCT ?s
            WHERE{ 
               ?s ?k ?v. 
               FILTER (?s = dbpedia:""" + word + """)
            }"""

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    try:
        url = results["results"]["bindings"][0]["s"]["value"]
    except:
        url = "No data found"

    return url

def getUrlByType(word, type):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = """
        PREFIX dbo:  <http://dbpedia.org/ontology/>
        PREFIX dbpedia: <http://dbpedia.org/resource/>
        SELECT DISTINCT ?s
        WHERE{ 
           ?s rdf:type dbo:""" + type + """. 
           FILTER (?s = dbpedia:""" + word + """)
        }"""

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    try:
        url = results["results"]["bindings"][0]["s"]["value"]
    except:
        url = "No data found"

    return url

already = []
list = range(len(entities))
j=0
for i in range(len(entities)):
    loop = i-j
    word = entities[loop][0]
    if word in already:
        entities.pop(loop)
        j+=1
        continue
    already.append(word)
    type = entities[loop][1]

    if type == 'PERSON':
        type = 'Person'
    if type == 'LOCATION':
        type = 'Location'
    if type == 'ORGANIZATION':
        type = 'Organisation'
    url = getUrlByType(word, type)
    if url == "No data found":
        url = getUrl(word)
        if url != "No data found":
            entities[loop].append(" Warning - on DBpedia this entity has different type")
    entities[loop].append(url)

import pprint

pprint.pprint(entities, width=200)

