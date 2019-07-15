import os
import requests
import logging
from bs4 import BeautifulSoup
import xml.dom.minidom

from lxml import etree
import xml.etree.ElementTree as ET

xsl_filename = "xyleme-objects.xsl"
parser = etree.XMLParser(remove_blank_text=False)
xslt_tree = etree.parse(xsl_filename, parser)
xslt_transformer = etree.XSLT(xslt_tree)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def xml_to_html(input_doc):
    original_tree = etree.fromstring(input_doc)
    output_doc = xslt_transformer(original_tree)
    return str(output_doc)

def pp_el(el):
    xml_data = xml.dom.minidom.parseString(ET.tostring(el).decode())
    return xml_data.toprettyxml()

def obj_to_dict(obj):
    obj_dict = {
        "tag": obj.__class__.__name__
    }
    obj_dict.update(obj.__dict__)
    return obj_dict

def get_xml_issues(el):
    issues = []

    # Check for bad tags
    if el.tag in ["Emph", "Underline", "Italic"]:
        issues.append("Found <strong>{}</strong> tag".format(el.tag))

    for e in list(el):
        issues += get_xml_issues(e)

    return issues

def get_html_issues(html):
    issues = []

    if '<br><br>' in html:
        issues.append("Found <strong>double newline</strong>")

    return issues


class SlideNote:
    def __init__(self, slidenote):
        logger.debug("__init__ slidenote")
        self.preview = xml_to_html(pp_el(slidenote))
        self.xml = pp_el(slidenote)

class SlideBodyElement:
    def __init__(self, slidebodyelement):
        logger.debug("__init__ slidebodyelement")
        self.preview = xml_to_html(pp_el(slidebodyelement))
        self.xml = pp_el(slidebodyelement)

class SlideBody:
    def __init__(self, slidebody):
        logger.debug("__init__ slidebody")
        self.elements = []
        self.issues = []

        for e in list(slidebody):
            self.elements.append(SlideBodyElement(e))

        if len(self.elements) > 1:
            self.issues.append("Slide has too many elements")

class Slide:
    def __init__(self, slide):
        logger.debug("__init__ slide")
        self.title = None
        self.body = None
        self.note = None
        self.theme = None
        self.issues = []

        if "slideTheme" in slide.attrib:
            self.theme = slide.attrib["slideTheme"]

        for e in list(slide):
            if e.tag == "Title":
                self.title = e.text
            elif e.tag == "Body":
                self.body = SlideBody(e)
                self.issues = get_xml_issues(e)
                
            elif e.tag == "SlideNote":
                self.note = SlideNote(e)
        
        for e in self.body.elements:
            self.issues += get_html_issues(e.preview)

class Topic:
    def __init__(self, topic):
        logger.debug("__init__ topic")
        self.title = None
        self.slide = None
        self.issues = []

        for e in list(topic):
            if e.tag == "Title":
                self.title = e.text
            elif e.tag == "ParaBlock":
                if len(list(e)) > 1:
                    self.issues.append("ParaBlock with multiple children")
                for p in list(e):
                    if p.tag == "Slide":
                        self.slide = Slide(p)
        
        if not self.title:
            self.issues.append("Missing title")
        if not self.slide:
            self.issues.append("Missing slide")

class Lesson:
    def __init__(self, lesson):
        logger.debug("__init__ lesson")
        self.title = None
        self.topics = []
        self.issues = []

        for e in list(lesson):
            if e.tag == "Topic":
                self.topics.append(Topic(e))
            elif e.tag == "Title":
                self.title = e.text
        
        if not self.title:
            self.issues.append("Missing title")
        if len(self.topics) == 0:
            self.issues.append("No topics")

class Module:
    def __init__(self, module):
        logger.debug("__init__ module")
        self.title = None
        self.lessons = []
        self.issues = []

        for e in list(module):
            if e.tag == "Lesson":
                self.lessons.append(Lesson(e))
            elif e.tag == "Title":
                self.title = e.text

        if not self.title:
            self.issues.append("Missing title")
        if len(self.lessons) == 0:
            self.issues.append("No lessons")

class IA:
    def __init__(self, ssp):
        logger.debug("__init__ ia")
        self.modules = []
        self.issues = []
        
        for e in list(ssp):
            if e.tag == "Modules":
                for m in list(e):
                    self.modules.append(Module(m))

class XylemeHelper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        r = self.session.get("https://vmware.xyleme.com/editor/j_spring_security_check")

        payload = {
            "j_username": self.username,
            "j_password": self.password,
        }

        r = self.session.post("https://vmware.xyleme.com/editor/j_spring_security_check", data=payload)

    def browse_repository(self, folderName):
        if folderName in [None, ""]:
            folderName = "/"
        
        dirName, baseName = os.path.split(folderName)

        folderName

        r = self.session.get("https://vmware.xyleme.com/editor/document/browseRepository", params={
            'folderName': folderName,
            'refresh': 'false'})

        data = r.json()
        data["folderName"] = folderName
        data["dirName"] = dirName
        data["baseName"] = baseName

        return data

    def get_ssp_raw(self, guid):
        r = self.session.get("https://sps-eu.xyleme.com/vmware/api/documents/{}/export/typed/download?exportMedia=false".format(guid))
        
        # If the response is not XML then it means we need
        # to submit the form to regenerate the content
        if r.text[:5] != "<?xml":
            soup = BeautifulSoup(r.text, features="html5lib")
            form = soup.find("form")
            posturl = form['action']
            fields = form.findAll('input')
            formdata = dict( (field.get('name'), field.get('value')) for field in fields)
            r = self.session.post(posturl, data=formdata)
        
        if r.status_code != 200:
            return None
        
        return r.text

    def get_ssp(self, guid):
        ssp = self.get_ssp_raw(guid)
        return ET.fromstring(ssp)

    def get_ssp_from_file(self, file_name):
        f = open(file_name, "r")
        ssp = f.read()
        return ET.fromstring(ssp)

    def ssp_to_ia(self, ssp):
        return IA(ssp)
