from datetime import datetime
import requests
import json
import uuid
from dateutil.relativedelta import relativedelta
from main import TIME_GET_CLIENT

async def new_client(best_server):

    print("TIME_GET_CLIENT:", TIME_GET_CLIENT)

    login_url = f"https://{best_server[0]}:{best_server[1]}/{best_server[4]}/login"
    print(f"!!!! LOGIN URL: {login_url}")

    username = best_server[5] + '_' + str(best_server[6])

    session = requests.Session()

    login = {
        'username': best_server[2],
        'password': best_server[3]
    }

    login_response = session.post(login_url, data=login, verify=False)

    if login_response.status_code == 200 and '3x-ui' in login_response.cookies:
        session_id = login_response.cookies['3x-ui']
        print(f'Успешная авторизация. Session ID: {session_id}')


        # Добавление клиента
        add_client_url = f"https://{best_server[0]}:{best_server[1]}/{best_server[4]}/panel/inbound/addClient"

        generated_uuid = str(uuid.uuid4())

        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [
                    {
                        "id": generated_uuid,
                        "flow": "xtls-rprx-vision",
                        "email": username,
                        "limitIp": 0,
                        "totalGB": 0,
                        "expiryTime": 0,
                        "enable": True,
                        "tgId": 0,
                        "subId": "",
                        "reset": 0
                    }
                ]
            })
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        add_client_response = session.post(add_client_url, headers=headers, json=payload, verify=False)

        if add_client_response.status_code == 200:
            print(f'Удалось создать новое подключение для {username}')
            # print('Ответ:', add_client_response.json())
        else:
            print(f"Не удалось создать подключение для {username}: {add_client_response.status_code}, {add_client_response.text}")


        get_inbound_url = f"https://{best_server[0]}:{best_server[1]}/{best_server[4]}/panel/api/inbounds/get/1"

        payload = {}
        headers = {
            'Accept': 'application/json'
        }

        get_inbound_response = session.get(get_inbound_url, headers=headers, data=payload, verify=False)

        if get_inbound_response.status_code == 200:
            print(f"Удалось получить информацию о соединении {username}")
            # print("Информация: ", get_inbound_response.json())
        else:
            print(f"Не удалось получить информацию о соединении: {get_inbound_response.status_code}, {get_inbound_response.text}")


        response_data = get_inbound_response.json()
        stream_setting_str = response_data["obj"]["streamSettings"]
        stream_setting_dict = json.loads(stream_setting_str)
        stream_settings = stream_setting_dict
        server_ip = best_server[0]
        public_key = stream_settings['realitySettings']['settings']['publicKey']
        fingerprint = stream_settings['realitySettings']['settings']['fingerprint']
        sni = stream_settings['realitySettings']['serverNames'][0]
        sid = stream_settings['realitySettings']['shortIds'][0]

        client_link = f"vless://{generated_uuid}@{server_ip}:443?type=tcp&security=reality&pbk={public_key}&fp={fingerprint}&sni={sni}&sid={sid}&spx=%2F&flow=xtls-rprx-vision#vless-reality-{username}"

        current_time = datetime.now()
        paid_up_to_time = current_time + relativedelta(TIME_GET_CLIENT)

        print("Заданное в TIME_GET_CLIENT:", TIME_GET_CLIENT)

        info_connections = [client_link, generated_uuid, server_ip, paid_up_to_time]

        return info_connections














