import requests
import json

# Configurações
ZABBIX_URL = "URL_Zabbix/zabbix/api_jsonrpc.php"
TOKEN = "TOKEN"

# Monta o payload da API
payload = {
    "jsonrpc": "2.0",
    "method": "hostgroup.get",
    "params": {
        "output": ["groupid", "name"]
    },
    "auth": TOKEN,
    "id": 1
}

# Envia requisição
response = requests.post(ZABBIX_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload))

# Exibe resultado
if response.status_code == 200:
    grupos = response.json().get("result", [])
    for grupo in grupos:
        print(f"{grupo['groupid']} - {grupo['name']}")
else:
    print("Erro ao consultar API:", response.status_code)
