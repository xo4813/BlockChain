import time
import datetime
import hashlib
import json


##거래 내역, 거래 수 가 필요하다.

class Block:
    def __init__(self):  # 여기 7개가 블록헤더(정체성), 채굴경쟁과 직접적연관이 되는 부분.
        self.prev_hash = None  # 현재블록이 이전 블록과 연결돼 있음을 나타내는 이전블록의 해시값을 포함하는 부분.
        self.timestamp = time.time()
        self.mrkl_root = None  # 거래가 몇 십개든 몇 백개든 몇 천개든 뭉쳐서 요약된 머클 루트의 용량은 32바이트로 항상 같다
        # '풀노드(full node)'가 될 수 있는데 이 머클트리의 이진트리 방식은 우리가 가지고 다니는 모바일로도 블록데이터의 일부만 다운받는 '라이트 노드(light node)'로서 쉽고 빠르게 특정 거래를 찾도록 해준다.
        # 이것이 머클트리가 블록에서 맡은 역할이다.
        # 머클트리에 넣을 트랜잭션
        self.bits = 4  # 난이도
        self.nounce = 0  # 빈도와 해시값 중복구분
        self.hash = None
        self.transactions = []  ##sd
        self.volume = 0
   
    def getHash(self):
        return self.hash

    def add_transaction(self, transaction):  # 트랜잭션 하나 받고 트랜잭션 리스트에 맨 뒤에 추가
        self.transactions.append(transaction)
        self.volume += 1

    def gen_mrkl_root(self):  # 머클루트 뽑아내기

        data_len = len(self.transactions)  # 트랜잭션 전체길이 뽑기
        tmp_merkle = []  # 머클트리에 트랜잭션 담기
        for t in self.transactions:
            tmp_merkle.append(t.hash)  # 머클트리에 들어가는 트랜잭션 하나씩 해시함수적용시키기

        if data_len % 2 != 0:  # 머클트리가 홀수면
            tmp_merkle.append(tmp_merkle[-1])  # 쌍을 이루지 못하는 마지막노드의 클론을 하나 생성해서 append

        if len(tmp_merkle) > 0:

            while len(tmp_merkle) > 0 and len(tmp_merkle) != 1:  # 루트를 뽑을때까지 loof
                tmp = []  # 머클노드가 append 될 임시 리스트

                for i in range(0, len(tmp_merkle), 2):
                    tmp.append(hashlib.sha256((tmp_merkle[i] + tmp_merkle[i + 1]).encode()).hexdigest())

                tmp_merkle = tmp

            self.mrkle_root = tmp_merkle[0]

            print("머클머클루트루트~!~!", self.mrkle_root)

        ##

    def gen_hash(self):
        while True:
            h = hashlib.sha256(self.toJSON().encode()).hexdigest()

            self.nounce += 1
            if h[:self.bits] == '0' * self.bits:
                self.hash = h
                print(h)
                break

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
