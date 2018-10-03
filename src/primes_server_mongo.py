import os
import json
import math
from flask import Flask, Response
from flask_mongoalchemy import MongoAlchemy
from mongoalchemy.document import Document, Index


app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'primes'
app.config['MONGOALCHEMY_SERVER'] = os.environ['MONGODB_HOST']
db = MongoAlchemy(app)


class Primes(db.Document):
    max_n = db.IntField()
    values = db.ListField(db.IntField())
    max_n_index = Index().ascending('max_n').unique()


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = int(math.sqrt(n))
    for k in range(3, d + 1, 2):
        if n % k == 0:
            return False
    return True


@app.route("/status")
def handle_status():
    return Response(json.dumps({
        'hostname': os.environ['HOSTNAME']
    }), mimetype='application/json')


@app.route("/primes/check/<number>")
def handle_is_prime(number):
    return Response(json.dumps({
        'hostname': os.environ['HOSTNAME'], 'number': int(number), 'isPrime': is_prime(int(number))
    }), mimetype='application/json')


@app.route("/primes/list/<max_n>")
def handle_prime_list(max_n):
    max_n = int(max_n)
    match = Primes.query.filter(Primes.max_n == max_n).first()
    primes = []
    if not match:
        primes = [] if max_n < 2 else [2]
        primes.extend([n for n in range(3, max_n + 1, 2) if is_prime(n)])
        Primes(max_n=max_n, values=primes).save()
    else:
        primes = match.values

    return Response(json.dumps({
        'hostname': os.environ['HOSTNAME'], 'max_n': int(max_n), 'primes': primes
    }), mimetype='application/json')
