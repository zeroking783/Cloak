import requests
import json
from datetime import datetime
from check_activity_users_daily import GB_GET_CLIENT

async def delete_client(session, ip, uuid, web_base_path):
    print(f"{uuid} in delete")

    delete_client_url = f"https://{ip}:65000/{web_base_path}/panel/api/inbounds/1/delClient/{uuid}"

    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    delete_client_response = session.post(delete_client_url, headers=headers, data=payload, verify=False)

    if delete_client_response.status_code == 200:
        print(f"Пользователь {uuid} удален")
        # print("Информация: ", get_inbound_response.json())
    else:
        print(
            f"Не удалось удалить пользователя {uuid}:\n {delete_client_response.status_code}, {delete_client_response.text}")


async def check_connections(row, db_serv, web_base_path):

    login_url = f"https://{row[4]}:65000/{web_base_path}/login"

    print(f"LOGIN_URL: {login_url}+ANAL")

    username = row[1] + '_' + str(row[0])

    print(f"USERNAME: {username}+ANAL")

    session = requests.Session()

    query_login = """
    SELECT login, pass FROM servers
    WHERE ip = $1
    """

    enter = await db_serv.fetchrow(query_login, row[4])

    print(f"Вот username server: {enter[0]}+ANAL\nВот password server: {enter[1]}+ANAL")

    login = {
        'username': enter[0],
        'password': enter[1]
    }

    print(f"LOGIN_ALL: {login}")

    login_response = session.post(login_url, data=login, verify=False)

    if login_response.status_code == 200 and '3x-ui' in login_response.cookies:
        session_id = login_response.cookies['3x-ui']
        print(f'Успешная авторизация. Session ID: {session_id}')

        # Если вышло время
        if row[5] < datetime.now():
            print("time plaki")
            await delete_client(session, row[4], row[3], web_base_path)
            return [1, 0]

        spent_gb = await refresh_spent_gb(session, row[4], username, web_base_path)

        if spent_gb >= GB_GET_CLIENT:
            print("gb plaki")
            await delete_client(session, row[4], row[3], web_base_path)
            return [2, 0]
        else:
            return [0, spent_gb]





async def refresh_spent_gb(session, ip, username, web_base_path):
    print(username)
    get_client_url = f"https://{ip}:65000/{web_base_path}/panel/api/inbounds/getClientTraffics/{username}"

    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    get_client_response = session.get(get_client_url, headers=headers, data=payload, verify=False)
    if get_client_response.status_code == 200:
        data = json.loads(get_client_response.text)
        print(data)

        up_volue = data['obj']['up']
        down_volue = data['obj']['down']

        spent_gb = int((up_volue + down_volue)/(1024**3))

        print(spent_gb)

        return spent_gb


