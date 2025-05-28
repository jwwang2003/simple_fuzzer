import random
from typing import Any


def insert_random_character(s: str) -> str:
    """
    向 s 中下标为 pos 的位置插入一个随机 byte
    pos 为随机生成，范围为 [0, len(s)]
    插入的 byte 为随机生成，范围为 [32, 127]
    """
    # TODO
    pos = random.randint(0, len(s))
    return s[:pos] + chr(random.randrange(32, 127)) + s[pos:]


def flip_random_bits(s: str) -> str:
    """
    基于 AFL 变异算法策略中的 bitflip 与 random havoc 实现相邻 N 位翻转（N = 1, 2, 4），
    从 s 中随机挑选一个 bit，将其与其后面 N - 1 位翻转（翻转即 0 -> 1; 1 -> 0）。
    注意：不要越界。
    """
    if not s:
        return s
    bin_str = "".join(f"{ord(c):08b}" for c in s)
    N = random.choice([1, 2, 4])
    pos = random.randint(0, len(bin_str) - N)
    flipped = "".join("1" if b == "0" else "0" for b in bin_str[pos : pos + N])
    bin_str = bin_str[:pos] + flipped + bin_str[pos + N :]
    result = "".join(
        chr(min(127, max(32, int(bin_str[i : i + 8], 2))))
        for i in range(0, len(bin_str), 8)
    )
    return result


# print(flip_random_bits("hello"))


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
    b = bytearray(s.encode())  # latin1 可让每个字符恰好映射到 0-255
    N = random.choice([1, 2, 4])
    if len(b) < N:
        return s  # 长度不足，无法操作
    start = random.randint(0, len(b) - N)  # 确保不会越界
    for i in range(N):
        delta = random.randint(-35, 35)
        original = b[start + i]
        mutated = (original + delta + 256) % 256
        b[start + i] = mutated
    return b.decode(errors="ignore")  # 还原为字符串


# print(arithmetic_random_bytes("hello"))


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
    interesting_2 = [
        0,
        1,
        16,
        32,
        64,
        127,
        128,
        255,
        256,
        512,
        1024,
        32767,
        32768,
        65535,
    ]
    interesting_4 = [
        0,
        1,
        16,
        32,
        64,
        127,
        128,
        255,
        32768,
        65535,
        2147483647,
        0x80000000,
        0xFFFFFFFF,
    ]

    N = random.choice([1, 2, 4])
    b = bytearray(s.encode())

    if len(b) < N:
        return s  # 不足 N 字节，跳过

    start = random.randint(0, len(b) - N)  # 确保不会越界
    # 选择对应 N 字节的 interesting 值
    if N == 1:
        val = random.choice(interesting_1)
        bytes_val = val.to_bytes(1, byteorder="little")
    elif N == 2:
        val = random.choice(interesting_2)
        bytes_val = val.to_bytes(2, byteorder="little", signed=False)
    else:  # N == 4
        val = random.choice(interesting_4)
        bytes_val = val.to_bytes(4, byteorder="little", signed=False)

    # 替换目标字节
    b[start : start + N] = bytes_val
    return b.decode(errors="ignore")


# print((interesting_random_bytes("hello")))


def havoc_random_insert(s: str):
    """
    基于 AFL 变异算法策略中的 random havoc 实现随机插入
    随机选取一个位置，插入一段的内容，其中 75% 的概率是插入原文中的任意一段随机长度的内容，25% 的概率是插入一段随机长度的 bytes
    """
    if not s:
        return s

    # 确定插入位置（0 到 len(s) 之间）
    insert_pos = random.randint(0, len(s))

    # 75% 概率插入原字符串的子串
    if random.random() < 0.75 and len(s) > 0:
        # 从原字符串中提取随机子串（长度 1-8 字节）
        max_len = min(8, len(s))
        substr_len = random.randint(1, max_len)
        start_idx = random.randint(0, len(s) - substr_len)
        insert_data = s[start_idx : start_idx + substr_len]
    else:
        # 25% 概率插入随机生成的可打印 ASCII 字符（32-126）
        rand_len = random.randint(1, 8)
        insert_data = "".join(
            chr(random.randint(32, 126)) for _ in range(rand_len)  # 可打印 ASCII 范围
        )
    # 执行插入操作并返回结果
    return s[:insert_pos] + insert_data + s[insert_pos:]


# print((havoc_random_insert("hello")))


def havoc_random_replace(s: str):
    """
    基于 AFL 变异算法策略中的 random havoc 实现随机替换
    随机选取一个位置，替换随后一段随机长度的内容，其中 75% 的概率是替换为原文中的任意一段随机长度的内容，25% 的概率是替换为一段随机长度的 bytes
    """
    if not s:
        return s
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
        replacement = "".join(chr(random.randint(32, 127)) for _ in range(rand_len))

    # 替换目标范围 [start : start + replace_len]
    return s[:start] + replacement + s[start + replace_len :]


# print((havoc_random_replace("hello")))


# ADD ON


def delete_random_bytes(s: str, min_length: int = 10) -> str:
    if len(s) <= min_length:
        return s
    delete_length = random.randint(1, len(s) - min_length)
    max_start_pos = len(s) - delete_length
    start_pos = random.randint(0, max_start_pos)
    return s[:start_pos] + s[start_pos + delete_length :]


def block_swap(input_str):
    swap_count = random.randint(1, 5)
    str_list = list(input_str)
    if len(str_list) <= 1:
        return input_str

    for _ in range(swap_count):
        # 随机选择块的大小，分为两部分后交换
        block_size = random.randint(1, len(str_list) // 2)
        first_start_index = random.randint(0, len(str_list) // 2 - block_size)
        second_start_index = random.randint(
            len(str_list) // 2, len(str_list) - block_size
        )
        block1 = str_list[first_start_index : first_start_index + block_size]
        block2 = str_list[second_start_index : second_start_index + block_size]
        str_list[first_start_index : first_start_index + block_size] = block2
        str_list[second_start_index : second_start_index + block_size] = block1
    mutated_input = "".join(str_list)
    return mutated_input


def change_case(s: str) -> str:
    N = random.choice([1, 2, 4])
    pos = 0
    if len(s) > N:
        pos = random.randint(0, len(s) - N)
    index = min(N, len(s))
    for i in range(index):
        char = s[pos + i]
        if char.isalpha():  # 检查字符是否是字母字符
            s = s[: pos + i] + char.swapcase() + s[pos + i + 1 :]  # 进行大小写转换
    return s


class Mutator:

    def __init__(self) -> None:
        """Constructor"""
        self.mutators = [
            insert_random_character,
            flip_random_bits,
            arithmetic_random_bytes,
            interesting_random_bytes,
            havoc_random_insert,
            havoc_random_replace,
            delete_random_bytes,
            block_swap,
            change_case,
        ]

    def mutate(self, inp: Any) -> Any:
        mutator = random.choice(self.mutators)
        return mutator(inp)