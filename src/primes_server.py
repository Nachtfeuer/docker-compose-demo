import os
import json
import math
from flask import Flask, Response
app = Flask(__name__)


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
    primes = [] if max_n < 2 else [2]
    primes.extend([n for n in range(3, max_n + 1, 2) if is_prime(n)])

    return Response(json.dumps({
        'hostname': os.environ['HOSTNAME'], 'max_n': int(max_n), 'primes': primes
    }), mimetype='application/json')
