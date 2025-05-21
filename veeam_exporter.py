import requests
import json
from prometheus_client import start_http_server, Gauge
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

veeam_backup_success = Gauge('veeam_backup_success', 'Nombre de sauvegardes réussies')
veeam_backup_failed = Gauge('veeam_backup_failed', 'Nombre de sauvegardes échouées')

veeam_server = "https://IP:9419/api/oauth2/token"
username = "USER"
password = "MOT DE PASSE"

def get_token():
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-version': '1.0-rev1'
    }
    response = requests.post(veeam_server, data=data, headers=headers, verify=False)
    return response.json()['access_token']

def get_veeam_metrics(token):
    url = "https://IP:9419/api/v1/jobs/states"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
        'x-api-version': '1.0-rev1'
    }

    response = requests.request("GET", url, headers=headers, verify=False)

    data = json.loads(response.text)

    success_count = 0
    failed_count = 0

    for job in data['data']:
        if job['lastResult'] == 'Success':
            success_count += 1
        else:
            failed_count += 1

    veeam_backup_success.set(success_count)
    veeam_backup_failed.set(failed_count)

if __name__ == '__main__':
    start_http_server(8000)

    while True:
        token = get_token()
        get_veeam_metrics(token)
        time.sleep(21550)
