# Author: Stephen Carter / stephendotcarter
import os
import requests
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

            
class XylemeHelper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        r = self.session.get(os.environ['XYLEME_API']+"/editor/j_spring_security_check")

        payload = {
            "j_username": self.username,
            "j_password": self.password,
        }

        r = self.session.post(os.environ['XYLEME_API']+"/editor/j_spring_security_check", data=payload)

    def browse_repository(self, folderName):
        if folderName in [None, ""]:
            folderName = "/"
        
        dirName, baseName = os.path.split(folderName)

        r = self.session.get(os.environ['XYLEME_API']+"/editor/document/browseRepository", params={
            'folderName': folderName,
            'refresh': 'false'
        })

        data = r.json()
        data["folderName"] = folderName
        data["dirName"] = dirName
        data["baseName"] = baseName

        return data

    def get_ssp_raw(self, guid):
        r = self.session.get(os.environ['XYLEME_MEDIA'] + "/api/documents/{}/export/typed/download".format(guid))
            
        # If the response is not XML then it means we need
        # to submit the form to regenerate the content
        if r.text[:5] != "<?xml":
            soup = BeautifulSoup(r.text, features="html5lib")
            form = soup.find("form")
            posturl = form['action']
            fields = form.findAll('input')
            formdata = dict((field.get('name'), field.get('value')) for field in fields)
            r = self.session.post(posturl, data=formdata)
        
        if r.status_code != 200:
            print('error')
            return None
        
        return r.text
