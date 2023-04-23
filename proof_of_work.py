# pow 模型主体代码
import time


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

    def proof_of_work(self):
        """工作量证明, 计算直到满足难度要求"""

    def add_to_chain(self):
        """将区块加入链"""


class mal_Block(Block):
    """恶意区块的类, 继承自Block"""
    def __init__(self, index, height, ph, status):
        super().__init__(index, height, ph, status)

    def mal_proof_of_work(self):
        """恶意区块的PoW"""

    def mal_add_to_chain(self):
        """将恶意区块加入链"""


def validate_chain():
    """检查链的有效性"""
