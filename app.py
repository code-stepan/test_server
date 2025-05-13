from flask import Flask, request, jsonify
import math
from bitarray import bitarray

app = Flask(__name__)

class BloomFilter(object):
    def __init__(self, size, number_expected_elements=100000):
        self.size = size
        self.number_expected_elements = number_expected_elements
        self.bloom_filter = bitarray(self.size)
        self.bloom_filter.setall(0)
        self.number_hash_functions = round((self.size / self.number_expected_elements) * math.log(2))

    # магия
    def _hash_djb2(self, s):
        hash = 5381
        for x in s:
            hash = ((hash << 5) + hash) + ord(x)
        return hash % self.size

    def _hash(self, item, K):
        return self._hash_djb2(str(K) + item)

    def add_to_filter(self, item):
        for i in range(self.number_hash_functions):
            self.bloom_filter[self._hash(item, i)] = 1

    def check_is_not_in_filter(self, item):
        for i in range(self.number_hash_functions):
            if self.bloom_filter[self._hash(item, i)] == 0:
                return True
        return False

bloom_filter = BloomFilter(1000000, 100000)


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "pong"})


@app.route('/bloom/add', methods=['POST'])
def bloom_add():
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({"error": "Key is required"}), 400

    bloom_filter.add_to_filter(str(data['key']))
    return jsonify({"status": "ok", "message": "Key added to Bloom filter"})


@app.route('/bloom/check', methods=['GET'])
def bloom_check():
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Key is required"}), 400

    is_not_present = bloom_filter.check_is_not_in_filter(str(key))
    return jsonify({
        "status": "ok",
        "key": key,
        "is_probably_present": not is_not_present,
        "is_definitely_not_present": is_not_present
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)