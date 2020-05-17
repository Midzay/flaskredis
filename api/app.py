from flask import Flask
from redis import Redis
from flask import request
import time
from flask import jsonify
from urllib.parse import urlparse
import re

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def hello():
    # redis.flushall()
    return '{} \n'.format(redis.zrange('domains', 0, -1, withscores=True))


@app.route('/visited_links', methods=['POST', 'GET'])
def post_links():
    data = request.json['links']
    for el in data:
        parser = urlparse(el)
        time_now = time.time()
        print (parser)
        if parser.netloc:
            redis.zadd("domains", mapping={
                parser.netloc + ' '+str(time_now): time_now}, nx=True)
        else:
            redis.zadd("domains", mapping={
                parser.path + ' '+str(time_now): time_now}, nx=True) 
    return jsonify(status=' ok')


@app.route('/visited_domains', methods=['POST', 'GET'])
def get_links():
    from_ = request.args.get('from')
    to_ = request.args.get('to')
    result = redis.zrangebyscore('domains', from_, to_, withscores=True)
    domains = []
    for el in result:
        domains.append(str(el[0].split()[0], 'utf-8'))
    domains = list(set(domains))
    return jsonify(domains=domains, status='ok')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
