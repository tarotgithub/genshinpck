import os


# 将字符串强制类型转化为数字
def hex_string_to_hex(hex_string):
    hex_num = 0
    i = 0
    for every_char in hex_string:
        hex_num = hex_num + every_char * 256 ** i
        i = i + 1
    return hex_num


# 将数字强制类型转化为bytes
def hex_to_hex_bytes(hex_num):
    # 先将其转化为bytes
    hex_bytes = []
    while hex_num > 256:
        single_hex_bytes = hex_num % 256
        hex_bytes = hex_bytes + [single_hex_bytes]
        hex_num = hex_num // 256

    single_hex_bytes = hex_num % 256
    hex_bytes = hex_bytes + [single_hex_bytes]

    return bytearray(hex_bytes)


if __name__ == '__main__':

    is_computer = input("是否为电脑：是：Y；否：N：")
    if is_computer == "Y":
        is_computer = True
    else:
        is_computer = False

    if is_computer:
        initial_offset = 0x0000003B
    else:
        initial_offset = 0x00000037

    pck_path = input("请输入pck文件地址：")
    if not os.path.exists(pck_path):
        print("该pck文件不存在！\n")
        os.system("pause")
        exit()

    new_pck_path = pck_path[0:-4:1] + "_new.pck"

    if os.path.exists(new_pck_path):
        print(os.path.split(new_pck_path)[1] + "已存在，请移除后再次操作")
        os.system("pause")
        exit()

    new_wav_path = input("请输入进行替换的wav文件地址：")

    if not os.path.exists(new_wav_path):
        print("该wav文件不存在！\n")
        os.system("pause")
        exit()

    target_wav_serial_num = input("请输入pck中被替换的wav文件序号：")
    target_wav_serial_num = int(target_wav_serial_num)

    with open(pck_path, "rb") as pck:
        with open(new_wav_path, "rb") as wav:
            with open(new_pck_path, "wb+") as new_pck:
                # 获取pck文件中包含的wav文件数量
                if is_computer:
                    pck.seek(0x00000038, 0)
                    pck_wav_num = hex_string_to_hex(pck.read(2))
                else:
                    pck.seek(0x00000034, 0)
                    pck_wav_num = hex_string_to_hex(pck.read(2))

                # 计算pck文件头部大小
                pck_head_size = initial_offset + pck_wav_num * 24
                # 将pck文件头部信息全部复制进new_pck中
                pck.seek(0, 0)
                new_pck.write(pck.read(pck_head_size))

                # 获取替换文件的大小
                new_wav_size = os.path.getsize(new_wav_path)
                # 获取被替换文件的大小
                pck.seek(initial_offset + target_wav_serial_num * 24 - 24 + 13, 0)
                pck_wav_size = hex_string_to_hex(pck.read(4))

                # 计算文件大小差值
                size_variation = new_wav_size - pck_wav_size

                # 对接下来new_pck头部信息进行调整
                for i_wav_site in range(target_wav_serial_num + 1, pck_wav_num + 1, 1):
                    # 调整文件起始点信息
                    new_pck.seek(initial_offset + i_wav_site * 24 - 24 + 17, 0)

                    i_new_pck_wav_site = hex_string_to_hex(new_pck.read(4))
                    i_new_pck_wav_site = i_new_pck_wav_site + size_variation

                    new_pck.seek(initial_offset + i_wav_site * 24 - 24 + 17, 0)
                    new_pck.write(hex_to_hex_bytes(i_new_pck_wav_site))

                # 调整文件大小信息
                new_pck.seek(initial_offset + target_wav_serial_num * 24 - 24 + 13, 0)
                new_pck.write(hex_to_hex_bytes(new_wav_size))

                # 复制实体wav数据到new_pck中
                # 计算target_wav之前的数据大小
                pck.seek(initial_offset + target_wav_serial_num * 24 - 24 + 17, 0)
                target_wav_site = hex_string_to_hex(pck.read(4))

                # 复制target_wav之前的数据
                pck.seek(pck_head_size, 0)
                new_pck.seek(0, 2)
                new_pck.write(pck.read(target_wav_site - pck_head_size))

                # 复制new_wav到target_wav_site
                wav.seek(0, 0)
                new_pck.seek(0, 2)
                new_pck.write(wav.read(-1))

                # 复制target_wav之后的信息
                pck.seek(0, 0)
                new_pck.seek(0, 2)
                new_pck.write(pck.read(-1)[target_wav_site + pck_wav_size:])
