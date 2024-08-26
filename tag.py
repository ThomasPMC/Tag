import requests
from datetime import datetime, timedelta
import pytz

# Remplacez par votre token API
API_TOKEN = '5a0fee4f0e9bdadafabdc51c6db96c1838ee4f9f'
BASE_URL_LEADS = f'https://api.pipedrive.com/v1/leads?api_token={API_TOKEN}'
UPDATE_LEAD_URL = 'https://api.pipedrive.com/v1/leads/{lead_id}?api_token=' + API_TOKEN
LABELS_URL = f'https://api.pipedrive.com/v1/leadLabels?api_token={API_TOKEN}'

# Dictionnaire pour associer les labels aux tags corrects
label_to_tag_map = {
    'FAQ': 0,
    'FUNDING': 1,
    "RODRIGO'S PROSPECTS": 2,
    "JASON'S PROSPECTS": 3,
    "JUAN'S PROSPECTS": 4,
    "WILFREDO'S PROSPECTS": 5,
    'NH TURNKEY SOLUTIONS': 6,
    "LAW FIRMS & PA'S": 7,
    'SUPPLIERS': 8,
    'EMAIL BLASTS': 9,
    'DEAD DEALS': 10,
}

# Calcul de la date limite (J-1) en UTC
utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
yesterday = utc_now - timedelta(days=1)

# Obtenir la liste des labels disponibles
labels_response = requests.get(LABELS_URL)
labels_data = labels_response.json().get('data', [])
label_map = {label['id']: label['name'] for label in labels_data}

start = 0
limit = 100  # Limite de 100 leads par page

while True:
    # Effectuer la requête pour récupérer les leads par lot
    url = f'{BASE_URL_LEADS}&start={start}&limit={limit}'
    response = requests.get(url)

    if response.status_code == 200:
        leads = response.json().get('data', [])

        if not leads:
            break  # Sortir de la boucle si aucun lead n'est renvoyé

        # Traiter les leads récupérés
        for lead in leads:
            lead_id = lead['id']
            add_time_str = lead.get('add_time')
            update_time_str = lead.get('update_time')
            label_ids = lead.get('label_ids', [])
            tag_value = lead.get('29dd25f6c89fc1336e88dc222673d47b521ff39d', None)

            # Conversion des chaînes de date en objets datetime (en UTC)
            add_time_dt = datetime.strptime(add_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc) if add_time_str else None
            update_time_dt = datetime.strptime(update_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc) if update_time_str else None

            # Obtenir les noms des labels à partir des IDs
            labels = [label_map.get(label_id, 'Unknown Label') for label_id in label_ids]

            # Filtrer les leads avec add_time ou update_time supérieur à J-1
            if (add_time_dt and add_time_dt > yesterday) or (update_time_dt and update_time_dt > yesterday):
                # Vérifier la correspondance entre le label et le tag
                for label in labels:
                    expected_tag = label_to_tag_map.get(label)
                    if expected_tag is not None and tag_value != expected_tag:
                        print(f"Lead ID: {lead_id} - Label: {label} - Tag actuel: {tag_value}, Tag attendu: {expected_tag}")
                        
                        # Mettre à jour le tag pour ce lead
                        update_data = {
                            '29dd25f6c89fc1336e88dc222673d47b521ff39d': expected_tag
                        }
                        update_response = requests.put(UPDATE_LEAD_URL.format(lead_id=lead_id), json=update_data)
                        
                        if update_response.status_code == 200:
                            print(f"Tag mis à jour pour le lead {lead_id} : {expected_tag}")
                        else:
                            print(f"Erreur lors de la mise à jour du lead {lead_id} : {update_response.json().get('error', 'Erreur inconnue')}")
                    else:
                        print(f"Lead ID: {lead_id} - Label: {label} - Tag correct : {tag_value}")

        start += limit  # Passer au lot suivant
    else:
        print(f"Erreur: {response.json().get('error', 'Une erreur est survenue')}")
        break

print("Traitement terminé.")
