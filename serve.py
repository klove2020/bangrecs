from flask import Flask, request, jsonify
import requests
from flask import redirect

from src.Backend.network.headers_f import add_cors_headers
from src.Backend.API.rec_dir.rec_f import get_rec_post
from src.Backend.API.trans_dir.trans_f import get_trans_post
from src.Backend.API.search_dir.search_f import get_search_post
from src.sql.query_f import get_effectivetags_list
from src.Backend.util.crypto import encrypt, decrypt
from src.Backend.API.F.dislike_f import dislike_post
from src.Backend.API.F.oauth_f import oauth_callback_fun
from src.Backend.util.logging_f import log_request

app = Flask(__name__)


@app.after_request
def cors_headers(response):
    return add_cors_headers(response)


@app.route('/api/v4/rec/<i>/', methods=['POST'])
# @profile
@log_request
def rec_v4_post(i):
    return get_rec_post(i, table_name="trans_ma")


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


# ## 后面弃用
@app.route('/api/v3/rec/<i>/', methods=['GET'])
def rec_v3(i):
    return jsonify({"message": "可以更新了，快催咕咕子更新 >_<，线上网址 bangrecs.net"})

# ## 后面弃用
@app.route('/api/v4/rec/<i>/', methods=['GET'])
def rec_v4(i):
    return jsonify({"message": "此API被弃用, 线上网址 bangrecs.net"})


if __name__ == '__main__':
    app.run(port=8085, debug=True)
    # app.run(port = 8085, use_reloader=False)
