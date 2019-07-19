import os, xmltodict
from flask import Flask, request, render_template, url_for

app = Flask(__name__)


@app.route("/editor/j_spring_security_check", methods=['GET','POST'])
def secCheck():
    return ""


@app.route("/api/documents/<guid>/export/typed/download")
def getCourse(guid):
    file = open('sample_module.xml', encoding='utf8')
    
    readFile = file.read()
    return readFile

