############################## Marcus Rônney ##############################
#Github: https://github.com/Marcusronney/zabbix_import_excel
#Linkedin: https://www.linkedin.com/in/marcus-r%C3%B4nney-627657bb/


#importando as bibliotecas do python
import os #montar as url dos arquivos
import pandas as pd #integrar ao excel
import requests #conectar via http na api do zabbix
import json #manipulação json



# Conectando ao Zabbix, coloque a url e token da api. O Token foi gerado no front do zabbix. >Configuração > Tokens da API > Criar Token
ZABBIX_URL = "URL_ZABBIX/zabbix/api_jsonrpc.php"
AUTH_TOKEN = "Token"

#Pega o Payload Json e realiza uma requisição para criar o host dentro do zabbix.
def create_host(auth_token, host_ip, host_name, display_name, group_ids, template_ids, description, dns_name, snmp_community):
    headers = {'Content-Type': 'application/json'}

    # Define a interface (Agent ou SNMP)
    if snmp_community:
        interface = {
            'type': 2,  # 1 Zabbix Agente, 2 SNMP, 3 IPMI, 4 JMX
            'main': 1,
            'useip': 1,
            'ip': host_ip,
            'dns': dns_name,
            'port': '161',
            'details': {
                'version': 2,
                'bulk': 0,
                'community': snmp_community
            }
        }
        tipo = "SNMP"
    else:
        interface = {
            'type': 1,  # Zabbix Agent
            'main': 1,
            'useip': 1,
            'ip': host_ip,
            'dns': dns_name,
            'port': '10050'
        }
        tipo = "Agent"

#Monta os parâmetros para a API
    params = {
        'host': host_name,
        'name': display_name,
        'description': description,
        'interfaces': [interface],
        'groups': [{'groupid': gid} for gid in group_ids]
    }

#Se houver algo na columa templates, adiciona a informação 
    if template_ids:
        params['templates'] = [{'templateid': tid} for tid in template_ids]

#Monta o payload para requisição
    payload = {
        'jsonrpc': '2.0',
        'method': 'host.create',
        'params': params,
        'auth': auth_token,
        'id': 1
    }


#Imprime os dados na tela.
    print(f"\n🔄 Criando host: {host_name} ({host_ip}) - Tipo: {tipo}")
    print(f"Grupos: {group_ids} | Templates: {template_ids or 'Nenhum'}")
    print(f"Descrição: {description}")
    print(f"DNS: {dns_name} | Comunnity: {snmp_community or 'N/A'}")


#Realiza a requisição para API
    response = requests.post(ZABBIX_URL, headers=headers, data=json.dumps(payload))

#Verifica a existência de Host para retorna o ID.
    if response.headers['Content-Type'].startswith('application/json'):
        try:
            result = response.json()
            if "result" in result:
                return result['result']
            elif "error" in result:
                print("❌ Erro da API Zabbix:", result['error']['data'])
                return None
        except json.JSONDecodeError as e:
            print(f"Erro de decodificação JSON: {e}")
            return None
    else:
        print("❌ Resposta inválida da API.")
        return None

#Carregando a planilha
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, 'Cadastra_HOSTS_Zabbix.xlsx')

    try:
        df = pd.read_excel(excel_file, dtype=str).fillna('')  # Garantir que campos vazios não virem NaN

#Coletando as tabelas da planilha
        for index, row in df.iterrows():

            # Coleta e sanitização de dados
            host_ip = str(row.get('IP', '')).strip()
            host_name = str(row.get('Nome_do_Host', '')).strip()
            display_name = str(row.get('Nome_Visivel', '')).strip()
            description = str(row.get('Descricao', '')).strip()
            dns_name = str(row.get('DNS', '')).strip()
            snmp_community = str(row.get('Comunnity', '')).strip()

            # Grupos
            group_ids = [int(gid.strip()) for gid in str(row.get('ID_Group', '')).replace('.', ',').split(',') if gid.strip().isdigit()]
            # Templates (opcional)
            template_ids = [int(tid.strip()) for tid in str(row.get('Template', '')).replace('.', ',').split(',') if tid.strip().isdigit()]

#Verifica se os campos obrigatórios estão preenchidos.
            if not host_ip or not host_name or not display_name or not group_ids:
                print(f"⚠️ Linha {index + 2}: Dados obrigatórios ausentes. Pulando...")
                continue

#Criando o Host.
            result = create_host(
                AUTH_TOKEN,
                host_ip,
                host_name,
                display_name,
                group_ids,
                template_ids,
                description,
                dns_name,
                snmp_community
            )

#Exibir resultos
            if result:
                print(f"✅ Host criado com sucesso! ID: {result['hostids'][0]}")
            else:
                print(f"❌ Falha ao criar host: {host_name} ({host_ip})")

    except FileNotFoundError:
        print(f"❌ Arquivo {excel_file} não encontrado.")
    except KeyError as e:
        print(f"❌ Coluna obrigatória ausente no Excel: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()