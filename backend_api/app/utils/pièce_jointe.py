import requests
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/file_analyzer")

API_KEY = '615c4a6af1614b4fef48d269eb0a221d19d61097a43a66c92b6ca02b3770eefb'
URL_UPLOAD = 'https://www.virustotal.com/api/v3/files'
URL_REPORT = 'https://www.virustotal.com/api/v3/analyses/'

def upload_file(file_path):
    headers = {
        'x-apikey': API_KEY
    }
    files = {'file': (file_path, open(file_path, 'rb'))}
    response = requests.post(URL_UPLOAD, headers=headers, files=files)

    if response.status_code == 200:
        analysis_id = response.json()['data']['id']
        print(f"Fichier soumis. ID d'analyse : {analysis_id}")
        return analysis_id
    else:
        print(f"Erreur lors de l'envoi du fichier : {response.json()}")
        return None


def get_report(analysis_id):
    headers = {'x-apikey': API_KEY}

    while True:
        response = requests.get(URL_REPORT + analysis_id, headers=headers)
        if response.status_code == 200:
            analysis_status = response.json()['data']['attributes']['status']
            if analysis_status == 'completed':
                return response.json()['data']['attributes']['results']
            else:
                print("Analyse en cours, attente de 10 secondes...")
                time.sleep(10)
        else:
            print(f"Erreur lors de la récupération du rapport : {response.json()}")
            return None
