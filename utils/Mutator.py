import math
import random
import struct
from typing import Any


def insert_random_character(s: str) -> str:
    """
    向 s 中下标为 pos 的位置插入一个随机 byte
    pos 为随机生成，范围为 [0, len(s)]
    插入的 byte 为随机生成，范围为 [32, 127]
    """
    # TODO
    return s


def flip_random_bits(s: str) -> str:
    """
    基于 AFL 变异算法策略中的 bitflip 与 random havoc 实现相邻 N 位翻转（N = 1, 2, 4），其中 N 为随机生成
    从 s 中随机挑选一个 bit，将其与其后面 N - 1 位翻转（翻转即 0 -> 1; 1 -> 0）
    注意：不要越界
    """
    # TODO
    pos = random.randint(0, len(s))  # 插入位置，包含 len(s) 表示可以插在最后
    rand_char = chr(random.randint(32, 127))  # 可打印 ASCII 字符
    s = s[:pos] + rand_char + s[pos:]
    return s

print(flip_random_bits("hello"))


def arithmetic_random_bytes(s: str) -> str:
    """
    基于 AFL 变异算法策略中的 arithmetic inc/dec 与 random havoc 实现相邻 N 字节随机增减（N = 1, 2, 4），其中 N 为随机生成
    字节随机增减：
        1. 取其中一个 byte，将其转换为数字 num1；
        2. 将 num1 加上一个 [-35, 35] 的随机数，得到 num2；
        3. 用 num2 所表示的 byte 替换该 byte
    从 s 中随机挑选一个 byte，将其与其后面 N - 1 个 bytes 进行字节随机增减
    注意：不要越界；如果出现单个字节在添加随机数之后，可以通过取模操作使该字节落在 [0, 255] 之间
    """
    # Convert string to mutable byte array
    b = bytearray(s.encode('latin1'))  # latin1 可让每个字符恰好映射到 0-255

    N = random.choice([1, 2, 4])
    if len(b) < N:
        return s  # 长度不足，无法操作

    start = random.randint(0, len(b) - N)  # 确保不会越界

    for i in range(N):
        delta = random.randint(-35, 35)
        original = b[start + i]
        mutated = (original + delta) % 256
        b[start + i] = mutated

    return b.decode('latin1')  # 还原为字符串

print(arithmetic_random_bytes("hello"))

def interesting_random_bytes(s: str) -> str:
    """
    基于 AFL 变异算法策略中的 interesting values 与 random havoc 实现相邻 N 字节随机替换为 interesting_value（N = 1, 2, 4），其中 N 为随机生成
    interesting_value 替换：
        1. 构建分别针对于 1, 2, 4 bytes 的 interesting_value 数组；
        2. 随机挑选 s 中相邻连续的 1, 2, 4 bytes，将其替换为相应 interesting_value 数组中的随机元素；
    注意：不要越界
    """
    # AFL 的 interesting 值
    interesting_1 = [0, 1, 16, 32, 64, 100, 127, 128, 255]
    interesting_2 = [0, 1, 16, 32, 64, 127, 128, 255, 256, 512, 1024, 32767, 32768, 65535]
    interesting_4 = [0, 1, 16, 32, 64, 127, 128, 255, 32768, 65535, 2147483647, 0x80000000, 0xFFFFFFFF]

    N = random.choice([1, 2, 4])
    b = bytearray(s.encode('latin1'))

    if len(b) < N:
        return s  # 不足 N 字节，跳过

    start = random.randint(0, len(b) - N)  # 确保不会越界

    # 选择对应 N 字节的 interesting 值
    if N == 1:
        val = random.choice(interesting_1)
        bytes_val = val.to_bytes(1, byteorder='little')
    elif N == 2:
        val = random.choice(interesting_2)
        bytes_val = val.to_bytes(2, byteorder='little', signed=False)
    else:  # N == 4
        val = random.choice(interesting_4)
        bytes_val = val.to_bytes(4, byteorder='little', signed=False)

    # 替换目标字节
    b[start:start+N] = bytes_val

    return b.decode('latin1')

print((interesting_random_bytes("hello")))


def havoc_random_insert(s: str):
    """
    基于 AFL 变异算法策略中的 random havoc 实现随机插入
    随机选取一个位置，插入一段的内容，其中 75% 的概率是插入原文中的任意一段随机长度的内容，25% 的概率是插入一段随机长度的 bytes
    """
    insert_pos = random.randint(0, len(s))

    if random.random() < 0.75 and len(s) > 1:
        # 75% 概率：插入来自原字符串的一段
        start = random.randint(0, len(s) - 1)
        end = random.randint(start + 1, min(start + 8, len(s)))  # 最多插入 8 字符
        insert_data = s[start:end]
    else:
        # 25% 概率：插入随机生成的一段
        rand_len = random.randint(1, 8)
        insert_data = ''.join(chr(random.randint(32, 127)) for _ in range(rand_len))

    return s[:insert_pos] + insert_data + s[insert_pos:]

print((havoc_random_insert("hello")))

def havoc_random_replace(s: str):
    """
    基于 AFL 变异算法策略中的 random havoc 实现随机替换
    随机选取一个位置，替换随后一段随机长度的内容，其中 75% 的概率是替换为原文中的任意一段随机长度的内容，25% 的概率是替换为一段随机长度的 bytes
    """
    start = random.randint(0, len(s) - 1)
    replace_len = random.randint(1, min(8, len(s) - start))  # 不越界

    if random.random() < 0.75 and len(s) > 1:
        # 75% 概率：用原文中的某段内容替换
        src_start = random.randint(0, len(s) - 1)
        src_end = random.randint(src_start + 1, min(src_start + replace_len, len(s)))
        replacement = s[src_start:src_end]
    else:
        # 25% 概率：用随机字节替换
        rand_len = replace_len
        replacement = ''.join(chr(random.randint(32, 127)) for _ in range(rand_len))

    # 替换目标范围 [start : start + replace_len]
    return s[:start] + replacement + s[start + replace_len:]

print((havoc_random_replace("hello")))


##ADD ON

def flip_random_bit(s: str) -> str:
    if not s:
        return s
    index = random.randint(0, len(s) - 1)
    c = ord(s[index])
    bit_to_flip = 1 << random.randint(0, 7)
    new_c = chr(c ^ bit_to_flip)
    return s[:index] + new_c + s[index+1:]

def delete_random_byte(s: str) -> str:
    if not s:
        return s
    index = random.randint(0, len(s) - 1)
    return s[:index] + s[index+1:]
class Mutator:

    def __init__(self) -> None:
        """Constructor"""
        self.mutators = [
            insert_random_character,
            flip_random_bits,
            arithmetic_random_bytes,
            interesting_random_bytes,
            havoc_random_insert,
            havoc_random_replace
        ]

    def mutate(self, inp: Any) -> Any:
        mutator = random.choice(self.mutators)
        return mutator(inp)
