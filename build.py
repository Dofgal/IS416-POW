# 运行相关代码
import threading
import time
from datetime import datetime
import sys
import os

import proof_of_work as pow


class Generate_block_thread(threading.Thread):
    """普通区块的线程类, 继承自threading.Thread父类"""
    
    def __init__(self, thread_num):
        threading.Thread.__init__(self)
        self.num = thread_num

    def run(self):
        """线程任务函数"""
        # 新建 Block对象
        block = pow.Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.Blockchain[-1].hash, 0)

        # 未能加入链时, 重新创建
        while not block.add_to_chain():
            block = pow.Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.Blockchain[-1].hash, 0)


class Generate_mal_block_thread(threading.Thread):
    """恶意区块的线程类"""
    
    def __init__(self, thread_num):
        threading.Thread.__init__(self)
        self.num = thread_num

    def run(self):
        # 最长链长度小于要求时, 不启动
        while len(pow.Blockchain) <= trigger:
            time.sleep(0.2)
        
        # 确定分叉的节点
        if len(pow.mal_node_chain) == 0:
            pow.mal_node_chain.append(pow.Blockchain[fork_pos])

        # 更新最长链, 并确定是否攻击成功
        pow.update_longest_chain()
        corrupted = False
        for block in pow.Blockchain:
            if block.status == 1:
                corrupted = True
                break
        
        # 攻击未成功, 将恶意区块链到分叉 mal_node_chain上
        if not corrupted:
            block = pow.mal_Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.mal_node_chain[-1].hash, 1)
            
            while not block.mal_add_to_chain(False):
                block = pow.mal_Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.mal_node_chain[-1].hash, 1)
        
        # 攻击成功, 将恶意区块链到最长链 Blockchain(即原来的分叉)上
        else:
            block = pow.mal_Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.Blockchain[-1].hash, 1)

            while not block.mal_add_to_chain(True):
                block = pow.mal_Block(len(pow.node_list) + 1, len(pow.Blockchain),pow.Blockchain[-1].hash, 1)


def build(total_node_num, normal_node_num):
    # 线程列表
    threads = []

    # 为所有普通区块创建线程
    for i in range(normal_node_num):
        threads.append(Generate_block_thread(i))

    # 恶意区块
    for i in range(normal_node_num, total_node_num):
        threads.append(Generate_mal_block_thread(i))

    # 启动多线程
    for thread in threads:
        thread.start()

    # 线程同步, 使主线程等待所有子线程完成任务
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    # 构造创世区块
    genesis = pow.Block(0, 0, '0', 0)
    pow.Blockchain.append(genesis)

    # 参数不足
    if len(sys.argv) < 3:
        print('格式: python build.py <节点总数> <恶意节点数量>')
        os._exit(1)
    
    # 接收输入参数, 包括区块总数和恶意区块的数量
    total_node_num = int(sys.argv[1])
    mal_node_num = int(sys.argv[2])
    normal_node_num = total_node_num - mal_node_num

    # 设置恶意区块的参数
    trigger = 5  # 足以触发攻击的区块链长度
    fork_pos = -2  # 在链上构造分支的位置
    
    # 如果普通节点数小于 trigger, 则不能设置恶意节点, 否则恶意节点将永久 sleep
    if total_node_num - mal_node_num < trigger and mal_node_num > 0:
        print('存在恶意节点时, 普通节点数量不可少于 5')
        os._exit(1)
    
    # 记录总时间
    ts0 = time.time()
    
    build(total_node_num, normal_node_num)
    
    # 更新并打印信息
    pow.update_longest_chain()
    print('====================最长链信息====================')
    corrupted = False
    for block in pow.Blockchain:
        create_time = datetime.fromtimestamp(block.time / 100)
        if block.status:
            stat = "\033[0;31m恶意\033[0m"
            corrupted = True
        else:
            stat = '普通'
        print('区块 %d\n性质: %s, 创建时间: %s, 所求得随机数: %d\n前驱哈希: %s\n自身哈希: %s\n' %
              (block.height, stat, create_time, block.nounce, block.prev_hash, block.hash))
    if corrupted:
        res = '\033[0;31m攻击成功\033[0m'
    else:
        res = '攻击失败'
    print('======================%s======================\n' %res)

    print('总用时: %6.4fs\n' % (time.time() - ts0))
