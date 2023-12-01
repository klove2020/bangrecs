from flask import jsonify, request
import requests
from flask import redirect
from src.Backend.util.crypto import encrypt,decrypt


def oauth_callback_fun():
    code = request.args.get('code')
    print(f"{code=}")
    state = request.args.get('state')
    # print(f"{state= }")
    if code:
        try:
            client_id = 'bgm276564fc2e63a9d1a'
            client_secret = 'bcacc55559fd46a967eb7b40828cde63'  # 你的 client secret
            redirect_uri = 'https://bangrecs.net/api/bangumi_oauth/callback'
            # redirect_uri = 'http://localhost:3000/bgmrec'

            payload = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
                "state":state
            }

            headers = {
                'User-Agent': 'bangrecs'
            }

            r = requests.post('https://bgm.tv/oauth/access_token', data=payload,  headers=headers)

            # print("test1")

            r.raise_for_status()
            response_data = r.json()
            # print(f"{response_data=}")

            # return jsonify(response_data)
        

            access_token = response_data.get('access_token', None)
            uid = response_data.get('user_id')
            # print(f"{access_token=}")

            if access_token:
                # 存储 access token 或执行其他操作
                
                tt = encrypt(f"{int(uid)}")
                # print(f"uid = {uid}")
                # return redirect(f'http://localhost:3000/bgmrec?utoken={tt}')
                return redirect(f'https://bangrecs.net/bgmrec/?utoken={tt}')
            else:
                return 'No access token in response', 400

        except requests.exceptions.RequestException as e:
            print(str(e))
            return str(e), 500
    else:
        return 'Bad request', 400
