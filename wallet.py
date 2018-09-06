from bitcoin import *
from transaction import *
from flask import Flask, render_template, request, jsonify
import requests
# 1. 나의 코인을 확인할 수 있어야 한다.
# 2. 코인을 송금할 수 있어야 한다.

class To_coin:
    def __init__(self):
        self.value=0
        self.to=""

    def set_coin(self, to, value):
        self.value = value
        self.to = to

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)


class Utxo:
    def __init__(self):
        self.tx_id=""
        self.n=0
        self.value=0
        self.address=""

    def set_utxo(self, txid, n, value, address):
        self.tx_id = txid
        self.n = n
        self.value = value
        self.address = address

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)

class Wallet:
    def __init__(self):
        self.priv=''
        self.pubk=''
        self.addr=''
        self.utxo_list=[]
        self.txout_list=[]
        self.total_coin=0
        self.remain_coin=0

    def gen_key(self, seed):
        self.priv = sha256(seed)
        self.pubk = privtopub(self.priv)
        self.addr = pubtoaddr(self.pubk)
        print("private key: "+self.priv)
        print("public key: "+self.pubk)
        print("addr: "+self.addr)

    def verify_utxo(self):
        # utxos=json.dumps("utxo:[{hash:abcd, n:2, value: 120, address: aaaa},{hash:efgh, n:1, value: 120, address: aaaa}]".,True)
        addr=json.dumps({"addr":self.addr})
        utxo_list_json=requests.post(url="http://127.0.0.1:8000/transactions/search_utxo", json=addr)
        print(utxo_list_json.text)
        utxo_list_json=json.loads(utxo_list_json.text)

        for u in utxo_list_json:
            utxo=Utxo()
            utxo.tx_id=u["tx_id"]
            utxo.n=u["n"]
            utxo.value=u["value"]
            utxo.address=u["address"]
            self.total_coin += utxo.value
            self.utxo_list.append(utxo)

        # utxo1=Utxo()
        # utxo1.set_utxo("abcd", 1, 120, "aaaa")  #test utxo 더미
        # utxo2=Utxo()
        # utxo2.set_utxo("efgh", 0, 120, "aaaa")   #test utxo 더미

        # self.utxo_list.append(utxo1)
        # self.utxo_list.append(utxo2)
        # utxos=json.load(pre_utxo)

        # for d in self.utxo_list:
        #     print("[verify_utxo] utxo : "+str(d))
        #     self.total_coin += d.value

        self.set_remain_coin()

    def send_tx(self):
        # 코인 전송을 누르면,
        # transaction을 만들고,
        # transaction의 in과 out을 설정해주고,
        # 블록체인 네트워크로 전송한다.

        tx=Transaction()

        utxos_to_json=json.dumps(self.utxo_list, default=lambda o: o.__dict__, sort_keys=True)
        tx.gen_txin(utxos_to_json, self.pubk)

        #남은 코인이 있다면 자기한테 보내는 txout 생성.
        if self.remain_coin > 0:
            txout_for_remain = To_coin()
            txout_for_remain.set_coin(self.addr, self.remain_coin)
            self.txout_list.append(txout_for_remain)

        #transaction에서 txout 생성.
        txout_list_json=json.dumps(self.txout_list, default=lambda  o: o.__dict__, sort_keys=True)
        tx.gen_txout(txout_list_json)

        self.total_coin=self.remain_coin

        tx.sign(self.priv)
        tx.gen_hash()

        # 이것을 시리얼화 해서
        tx_json=json.dumps(tx, default=lambda o:o.__dict__, sort_keys=True)
        # 블록체인에 전송
        print("create transaction : "+tx_json)
        requests.post("http://localhost:8000/transactions/new", json=tx_json)

    def add_txout(self, to, value):
        value=int(value)

        if self.remain_coin < value:
            return False

        self.remain_coin-=value
        to_coin=To_coin()
        to_coin.set_coin(to, value)
        self.txout_list.append(to_coin)
        return True

    def delete_txout(self):
        self.txout_list.clear()
        self.set_remain_coin()

    def set_remain_coin(self):
        self.remain_coin = self.total_coin


#####################################################################################################################
# 웹 상에서 wallet에 접속하기 위한
#####################################################################################################################

app = Flask(__name__)
w = None

@app.route('/wallet')
def wallet():
    return render_template("wallet.html")

@app.route('/mywallet', methods=["post"])
def mywallet():
    global w
    w = Wallet()
    seed = request.form["seed"]
    w.gen_key(seed)
    w.verify_utxo()
    return render_template("mywallet.html", balance=w.total_coin, address=w.addr)

@app.route("/add_tx", methods=["post"])
def add_tx():
    address = request.form["to_address"]
    value = request.form["to_value"]
    add_result = w.add_txout(address, value)

    if add_result:
        return jsonify(result="success", balance=w.remain_coin)
    else :
        return jsonify(result="false")

@app.route("/commit_tx")
def commit_tx():
    w.send_tx()
    return jsonify(result="success", balance=w.remain_coin)

@app.route("/delete_tx")
def delete_tx():
    w.delete_txout()
    return jsonify(result="success", balance=w.remain_coin)

def main():
    w=Wallet()
    seed="khk"
    w.gen_key(seed)
    w.verify_utxo()
    w.add_txout("bbbb",200)
    w.send_tx()


if __name__ == "__main__" :
     # main()
     app.run(host='0.0.0.0', port=81)
