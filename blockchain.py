from flask import Flask, render_template, request, jsonify
from transaction import *
import threading
import time
from block import Block
import wallet

class BlockChain:

    def __init__(self):
        self.isMinng = False
        self.chain = []
        self.curren_transactions = []
        #genesis_bolck.bits = 5  # 초기 난이도
       

    def startThreading(self):
        genesis_bolck = Block()
        coin_base = Transaction()
        coin_base_output = wallet.To_coin()
        coin_base_output.set_coin("1Hzw9arvpZjaTN6UkfzKBCYbyAaePe8viZ", 50)
        coin_base.gen_coinbase_txout(str(coin_base_output))
        coin_base.gen_hash()
        genesis_bolck.add_transaction(coin_base)
        genesis_bolck.gen_hash()
        self.chain.append(genesis_bolck)
        while True:
            print('채굴 시작 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            start_time = time.time()
            newBlock = self.create_block()

            newBlock.gen_hash()


            self.chain.append(newBlock)
            print("채굴 끝 --- %s seconds ---" %(time.time() - start_time))
            # self.findyourbalance('aaa')
            # 새로운 블록 생성

    def mining(self):
        # print('new start')

        if self.isMinng == False:
            self.isMinng = True
            # print('new block')

            self.t1 = threading.Thread(target=self.startThreading)
            self.t1.daemon = True
            self.t1.start()

    # 새로운 블록생성
    def create_block(self):
        # 1. 이전 블럭의 해쉬값을 구함
        previous_hash = self.chain[-1].getHash()

        # 2. 새로운 블럭 생성
        cb = Block()

        coin_base = Transaction()
        coin_base_output = wallet.To_coin()
        coin_base_output.set_coin("1Hzw9arvpZjaTN6UkfzKBCYbyAaePe8viZ", 50)
        coin_base.gen_coinbase_txout(str(coin_base_output))
        coin_base.gen_hash()
        cb.add_transaction(coin_base)

        # tra = Transaction()
        # txin = TxIn()
        # txin.set_Txin(' askdlfjaelifhjoalwiejrh',1,100,'awefarg324wer','awer23rawesrf')
        #
        # txout = TxOut()
        # txout.set_txout('aweradsfraeawd',100)
        #
        # tra.inputs.append(txin)
        # tra.outputs.append(txout)
        #
        # self.curren_transactions.append(tra)
        # self.curren_transactions.append(tra)
        # self.curren_transactions.append(tra)
        # self.curren_transactions.append(tra)
        # self.curren_transactions.append(tra)


        # 3. 지금까지의 트랜젝션 블록에게 이전함
        for i,val  in enumerate(self.curren_transactions):
            print(self.chain.__len__())
            tr = self.curren_transactions[i]
            cb.add_transaction(tr)

        self.curren_transactions.clear()
        #cb.gen_mrkl_root()
        # 4. 새로운 블럭에 이전 블럭의 해쉬값을 주입
        cb.prev_hash = previous_hash

        return cb

    # 남은 잔액 찾기
    def findyourbalance(self,address):
        print('findyourbalance')

        utxos = []

        for chainBlock in self.chain:#1.블록체인별로
            for transaction in chainBlock.transactions: #2.트랜잭션을 검사해서
                for i,tr_output in enumerate(transaction.outputs):
                    if tr_output.to == address: #3.입력된 wallet주소 값을 찾는다.
                        utxo = wallet.Utxo()
                        utxo.set_utxo(transaction.tx_id,i,tr_output.value,tr_output.to)
                        utxos.append(utxo)
                        print(utxos)

        for chainBlock in self.chain:  #4.블록별로
            for transaction in chainBlock.transactions:#5.트랜잭션을 검사해서
                for tr_input in transaction.inputs:
                    for utxo in utxos:
                        if utxo.tx_id == tr_input.pre_tx_id:
                             utxos.remove(utxo)

        return json.dumps(utxos, default=lambda o : o.__dict__, sort_keys=True)
        
if __name__ == '__main__':

    # 서버 시작
    app = Flask(__name__)

    # 새로운 트랜젝션
    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        tx=json.loads(request.json)
        tran=Transaction()
        tran.json_to_tran(tx)
        bc.curren_transactions.append(tran)
        return "true"

    @app.route('/transactions/search_utxo', methods=['POST'])
    def search_utxo():
        get_addr=json.loads(request.json)
        addr=get_addr["addr"]
        utxo_json=bc.findyourbalance(addr)
        print("request search utxo : " + utxo_json)
        return str(utxo_json)

    @app.route('/block')
    def block():
        number = request.args.get('number')
        result = bc.chain[int(number)]
        return render_template("index.html",result = result, number = number)


    @app.route("/")
    def index():
        result = bc.chain
        return render_template("index2.html",result = result)

    bc = BlockChain()
    bc.mining()
  
    app.run(host='127.0.0.1', port=8000)
