import aiohttp
import asyncio

API_KEY = '615c4a6af1614b4fef48d269eb0a221d19d61097a43a66c92b6ca02b3770eefb'
URL_UPLOAD = 'https://www.virustotal.com/api/v3/files'
URL_REPORT = 'https://www.virustotal.com/api/v3/analyses/'

async def upload_file(file_path):
    headers = {
        'x-apikey': API_KEY
    }
    files = {'file': (file_path, open(file_path, 'rb'))}
    
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file_data:
            form = aiohttp.FormData()
            form.add_field('file', file_data, filename=file_path)
            async with session.post(URL_UPLOAD, headers=headers, data=form) as response:
                if response.status == 200:
                    response_data = await response.json()
                    analysis_id = response_data['data']['id']
                    print(f"Fichier soumis. ID d'analyse : {analysis_id}")
                    return analysis_id
                else:
                    error = await response.json()
                    print(f"Erreur lors de l'envoi du fichier : {error}")
                    return None

async def get_report(analysis_id):
    headers = {'x-apikey': API_KEY}

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(URL_REPORT + analysis_id, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    analysis_status = response_data['data']['attributes']['status']
                    if analysis_status == 'completed':
                        print("Analyse terminée.")
                        return response_data['data']['attributes']['results']
                    else:
                        print("Analyse en cours, attente de 10 secondes...")
                        await asyncio.sleep(10)
                else:
                    error = await response.json()
                    print(f"Erreur lors de la récupération du rapport : {error}")
                    return None
