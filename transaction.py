import json
from bitcoin import *

class TxIn:
    def __init__(self):
        self.pre_tx_id=None #사용할 UTX0가 포함된 트랜잭션의 해시
        self.n=0 # 위 트랜잭션 중에서 몇번째 UTX0인지
        self.value='' #위 UTX0의 잔액
        self.address='' #위 UTX0의 수신주소 (공개키 해시)
        self.pubk='' #사용자의 공개키
        self.sign=None #서명

    def set_Txin(self, pre_tx_in, n, value, address, pubk):
        self.pre_tx_id = pre_tx_in
        self.n = n
        self.value = value
        self.address = address
        self.pubk = pubk

    def gen_sign(self, priv):
        self.sign=ecdsa_sign(self.make_plaintext(), priv) #얘가 평문을 해시도 해주고, 싸인도 해준다.

    def make_plaintext(self):
        return json.dumps({"hash":self.pre_tx_id, "n":self.n, "value":self.value, "address":self.address, "pubk":self.pubk}, sort_keys=True)

    def verify_sign(self):
        return ecdsa_verify(self.make_plaintext(), self.sign, self.pubk)

    def can_spend(self):
        if self.address == pubtoaddr(self.pubk):
            return True

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)
    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)

class TxOut:
    def __init__(self):
        self.to='' #받는 사람 주소
        self.value=''

    def set_txout(self, to, value):
        self.to=to
        self.value=value

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)
    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)


class Transaction:
    def __init__(self):
        self.vin_sz=0
        self.vout_sz=0
        self.tx_id=None
        self.inputs=[]
        self.outputs=[]
        self.time=time.time()

    def gen_txin(self, utxo, pubk):
        utxo=json.loads(utxo)
        print("[gen_txin] utxo : "+str(utxo))
        for u in utxo:
            txin= TxIn()
            txin.set_Txin(u["tx_id"], u["n"], u["value"],  u["address"], pubk)
            self.inputs.append(txin)
            self.vin_sz+=1

    def gen_txout(self, txout_list):
        txout_list=json.loads(txout_list)
        print("[gen_txout] txout_list : "+str(txout_list))
        for i in txout_list:
            txout=TxOut()
            to=i["to"]
            value=i["value"]
            txout.set_txout(to, value)
            self.outputs.append(txout)
            self.vout_sz+=1

    def gen_coinbase_txout(self, coinbase_txout):
        coinbase_txout=json.loads(coinbase_txout)
        txout=TxOut()
        to=coinbase_txout["to"]
        value=coinbase_txout["value"]
        txout.set_txout(to, value)
        self.outputs.append(txout)
        self.vout_sz+=1

    def can_spent(self):
        for txin in self.inputs:
            #서명이 pubk로 풀리는가
            txin.verify_sign()
            #pubk 키의 해쉬가 address가 맞나.
            if ~txin.can_spend():
                return False

    def gen_hash(self):
        tx=self.toJSON()
        print("gen_hash : "+tx)
        self.tx_id=sha256(tx)
        print("gen_hash tx_id : "+self.tx_id)

    def sign(self, priv):
        for txin in self.inputs:
            txin.gen_sign(priv)

    def json_to_tran(self, tx_json):
        self.vin_sz=tx_json["vin_sz"]
        self.vout_sz=tx_json["vout_sz"]
        self.tx_id=tx_json["tx_id"]

        for tin in tx_json["inputs"]:
            txin= TxIn()
            txin.pre_tx_id=tin["pre_tx_id"]
            txin.n =tin["n"]
            txin.value =tin["value"]
            txin.address =tin["address"]
            txin.pubk =tin["pubk"]
            txin.sign =tin["sign"]
            self.inputs.append(txin)
        for tout in tx_json["outputs"]:
            txout=TxOut()
            txout.to=tout["to"]
            txout.value=tout["value"]
            self.outputs.append(txout)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)
    def __str__(self):
        return self.toJSON()

if __name__ =="__main__":
    pass