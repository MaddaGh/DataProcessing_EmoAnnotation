from rdflib import *
from rdflib.graph import Graph
import re

modelet2 = Graph()
modelet2.parse("C:/Users/ghiot/Documents/TESI/ontologies/meaw_inf.ttl", format="ttl")


with open("C:/Users/ghiot/Documents/TESI/ontologies/meaw_inf.ttl", "r", encoding="utf-8") as file:
    ttl_text = file.read()

new_iri = "https://raw.githubusercontent.com/MaddaGh/DataProcessing_EmoAnnotation/main/meaw.ttl#"
pattern1 = re.compile(r'http://www.semanticweb.org/ghiot/ontologies/2023/11/meaw/')
pattern2 = re.compile(r'http://www.semanticweb.org/ghiot/ontologies/2023/11/meaw#')
pattern3 = re.compile(r'http://www.semanticweb.org/ghiot/ontologies/2024/0/untitled-ontology-64#')
pattern4 = re.compile(r'http://www.semanticweb.org/ghiot/ontologies/2024/0/untitled-ontology-65#')

# Substitute the matched pattern with a replacement string
modified_text = pattern1.sub(new_iri, ttl_text)
modified_text = pattern2.sub(new_iri, modified_text)
modified_text = pattern3.sub(new_iri, modified_text)
modified_text = pattern4.sub(new_iri, modified_text)

print(modified_text)

modelet = Graph()
modelet.parse(data=modified_text, format="turtle")
print(modelet)

meaw = Namespace("https://raw.githubusercontent.com/MaddaGh/DataProcessing_EmoAnnotation/main/meaw.ttl#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
modelet.bind("meaw", meaw)
modelet.bind("rdfs", rdfs)
modelet.bind("owl", owl)
modelet.bind("rdf", rdf)
modelet.bind("xsd", xsd)

modelet.serialize(destination="C:/Users/ghiot/Documents/TESI/ontologies/meaw.ttl", format="ttl")

