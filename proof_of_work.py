# pow 模型主体代码
import time
import hashlib
import threading
import os

Blockchain = []  # 最长链
node_list = []  # 所有区块节点的集合
mal_node_chain = []  # 恶意节点构造的分叉

thre = 2**239  # PoW的难度衡量


class Block():
    """普通区块节点的类"""
    def __init__(self, index, height, ph, status):
        self.index = index  # 节点编号，唯一
        self.height = height  # 节点高度
        self.prev_hash = ph  # 前驱节点哈希
        self.time = int(round(time.time(), 2) * 100)  # 创建时间
        self.nounce = 0  # 待计算随机数
        self.hash = '0'  # 哈希结果
        self.status = status  # 节点性质：0普通、1恶意

    def calc_hash(self):
        """对区块的前驱哈希、创建时间、随机数计算哈希: sha256(sha256())"""
        str_to_hash = self.prev_hash + hex(self.time)[2:] + hex(
            self.nounce)[2:]  # 16进制形式的字符串
        single_hash = hashlib.sha256(str_to_hash.encode()).hexdigest()
        self.hash = hashlib.sha256(single_hash.encode()).hexdigest()
        return self.hash

    def proof_of_work(self):
        """工作量证明, 计算直到满足难度要求"""
        curr_len = len(Blockchain)
        while int(self.calc_hash(), 16) > thre:
            self.nounce += 1

        # 已有新区块加入，重新计算
        if (curr_len < len(Blockchain)):
            return False
        else:
            return True

    def add_to_chain(self):
        """将区块加入链"""
        if self.proof_of_work():
            update_longest_chain()  # 更新最长链
            validate_chain()  # 验证链的有效性

            # 加入最长链和区块节点集
            node_list.append(self)
            Blockchain.append(self)

            ts_prev = Blockchain[-1].time / 100
            self.index = len(node_list)
            print("区块 %d -- 创建所花时间 %6.4f(s), 线程 %s\n" %
                  (self.index, time.time() - ts_prev,
                   threading.current_thread().name))

            return True
        else:
            return False


class mal_Block(Block):
    """恶意区块的类, 继承自Block"""
    def __init__(self, index, height, ph, status):
        super().__init__(index, height, ph, status)

    def mal_proof_of_work(self, corrupted):
        """恶意区块的PoW"""
        if not corrupted:  # 攻击未成功时，检查 mal_node_chain
            target = mal_node_chain
        else:  # 攻击成功后，检查 Blockchain
            target = Blockchain
        mal_len = len(target)

        while int(self.calc_hash(), 16) > thre:
            self.nounce += 1

        # 已有新区快加入，重新计算
        if mal_len < len(target):
            return False
        else:
            return True

    def mal_add_to_chain(self, corrupted):
        """将恶意区块加入链"""
        if self.mal_proof_of_work(corrupted):
            update_longest_chain()
            validate_chain()

            node_list.append(self)
            if not corrupted:  # 攻击未成功时，加入恶意分叉
                mal_node_chain.append(self)
            else:  # 攻击成功后，加入最长链
                Blockchain.append(self)

            ts_prev = Blockchain[-1].time / 100
            self.index = len(node_list)
            print("\033[0;31m恶意区块\033[0m %d -- 创建所花时间 %6.4f(s), 线程 %s\n" %
                  (self.index, time.time() - ts_prev,
                   threading.current_thread().name))

            return True
        else:
            return False


def update_longest_chain():
    """更新最长链Blockchain"""
    tmp_chain = []
    tmp_chain.append(Blockchain[0])

    parent = tmp_chain[0]
    fork_list = []  # 所有分叉的列表

    # 无分叉且所有区块全部上链时结束循环
    while len(tmp_chain) < len(node_list):
        # 统计区块的后继数量
        cnt = 0
        for node in node_list:
            if node.prev_hash == parent.hash:
                tmp_chain.append(node)
                cnt += 1

        if cnt == 0:  # 末尾区块
            break
        elif cnt == 2:  # 分叉所在
            fork_list.append([tmp_chain.pop()])
            fork_list.append([tmp_chain.pop()])
            break
        else:
            parent = tmp_chain[-1]

    # 分别查找分叉
    for fork in fork_list:
        parent = fork[0]
        fork_len = 0
        while fork_len < len(fork):
            fork_len = len(fork)
            for node in node_list:
                if node.prev_hash == parent.hash:
                    fork.append(node)
                    parent = node

    # 存在分叉时，将最长分叉拼接到主链上
    if fork_list:
        # 更新节点信息
        for fork in fork_list:
            for n in fork:
                n.height = len(tmp_chain) + fork.index(n)

        for node in node_list:
            node.index = node_list.index(node) + 1

        longest_fork = max(fork_list, key=len)
        tmp_chain.extend(longest_fork)

        Blockchain.clear()
        Blockchain.extend(tmp_chain)


def validate_chain():
    """检查链的有效性"""
    prev_hash = Blockchain[0].hash
    for block in Blockchain[1:]:
        # 前驱哈希一致性检查
        if block.prev_hash != prev_hash:
            print("前驱哈希不一致: 区块 %d\n" % block.index)
            os._exit(1)

        # PoW正确性检查
        if int(block.calc_hash(), 16) > thre:
            print("PoW不通过: 区块 %d\n" % block.index)
            os._exit(1)
        prev_hash = block.hash
