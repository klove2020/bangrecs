from flask import Flask, request, jsonify
import requests
from flask import redirect
import json

from src.Backend.network.headers_f import add_cors_headers
from src.Backend.API.rec_dir.rec_f import get_rec_post
from src.Backend.API.trans_dir.trans_f import get_trans_post
from src.Backend.API.search_dir.search_f import get_search_post
from src.sql.query_f import get_effectivetags_list
from src.Backend.util.crypto import encrypt, decrypt
from src.Backend.API.F.dislike_f import dislike_post
from src.Backend.API.F.oauth_f import oauth_callback_fun
from src.Backend.util.logging_f import log_request
from src.Backend.API.rec_dir.rec4client_f import get_rec_app
from src.Backend.API.rec_dir.rec4app2_f import get_rec_app2

from src.Backend.API.app_f import app
# app = Flask(__name__)


@app.after_request
def cors_headers(response):
    return add_cors_headers(response)


@app.route('/api/v4/rec/<i>/', methods=['POST'])
# @profile
@log_request
def rec_v4_post(i):
    return get_rec_post(i, table_name="trans_ma")


@app.route('/api/v4/rec4app/<i>/', methods=['GET'])
@log_request
def rec_v4_app(i):
    return get_rec_app(i, table_name="trans_ma")


@app.route('/api/v4/rec4app2/<i>/', methods=['POST'])
@log_request
def rec_v4_app2(i):
    return get_rec_app2(i, table_name="trans_ma")


@app.route('/api/v4/rec_dev/<i>/', methods=['POST'])
# @profile
def rec_v4_post_dev(i):
    return get_rec_post(i, table_name="trans_ma_processing")


@app.route('/api/v4/trans/<i>/', methods=['POST'])
@log_request
def trans_post(i):
    return get_trans_post(i, trans_ma_name="trans_ma")


@app.route('/api/v4/search/', methods=['POST'])
# @profile
@log_request
def search_post():
    return get_search_post()


@app.route('/api/v4/tags_list/', methods=['GET'])
def get_tag_list():
    return get_effectivetags_list()


@app.route('/api/dislike', methods=['POST'])
def dislike_func():
    return dislike_post()


# oauth
@app.route('/api/bangumi_oauth/callback', methods=['GET'])
def oauth_callback():
    return oauth_callback_fun()


@app.route('/api/utoken2uid', methods=['GET'])
def local_oauth_callback():
    utoken = request.args.get('utoken')
    print(f"{utoken=}")
    uid = decrypt(utoken)

    return jsonify({"uid": uid})


# 弃用
@app.route('/api/v3/rec/<i>/', methods=['GET'])
def rec_v3(i):
    return jsonify({"message": "可以更新了，快催咕咕子更新 >_<，线上网址 bangrecs.net"})

# 弃用
@app.route('/api/v4/rec/<i>/', methods=['GET'])
def rec_v4(i):
    return jsonify({"message": "此API被弃用, 线上网址 bangrecs.net"})


# if __name__ == '__main__':
#     app.run(port=8085, debug=True)
#     # app.run(port = 8085, use_reloader=False)



# test
# @profile
def test_post_request():
    with app.test_client() as client:
        # 您提供的JSON数据
        data = {
            "type": 6,
            "update_f": True,
            "strategy": "p",
            "IsTimeFilter": False,
            "IsTagFilter": False,
            "startDate": "2020-01-30",
            "endDate": "2024-01-30",
            "topk": 10,
            "popdays": 7,
            "collects": [
                {
                    "updated_at": "2024-01-28T01:08:41+08:00",
                    "comment": "xxx",
                    "subject_id": 147068,
                    "subject_type": 2,
                    "vol_status": 0,
                    "ep_status": 0,
                    "type": 2,
                    "rate": 10
                },
                {
                    "updated_at": "2024-01-28T01:09:41+08:00",
                    "comment": "xxx",
                    "subject_id": 876,
                    "subject_type": 2,
                    "vol_status": 0,
                    "ep_status": 0,
                    "type": 2,
                    "rate": 0
                },
                {
                    "updated_at": "2024-01-28T01:09:41+08:00",
                    "comment": "xxx",
                    "subject_id": 2600,
                    "subject_type": 6,
                    "vol_status": 0,
                    "ep_status": 0,
                    "type": 2,
                    "rate": 0
                },
            ]
        }

        data_json = json.dumps(data)
        
        # 注意: 如果您的端点需要其他类型的头部（如认证信息），请相应地添加
        response = client.post('/api/v4/rec4app2/klove/', data=data_json, content_type='application/json')

        decoded_data = response.data.decode('utf-8')
        response_dict = json.loads(decoded_data)
        print(json.dumps(response_dict, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test_post_request()