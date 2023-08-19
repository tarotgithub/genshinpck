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
    if is_computer == "Y" or is_computer == 'y':
        is_computer = True
    elif is_computer == "N" or is_computer == 'n':
        is_computer = False
    else:
        print('输入错误！')
        os.system('pause')
        exit()

    if is_computer:
        initial_offset = 0x0000003B
    else:
        initial_offset = 0x00000037

    pck_dir_path = input("请输入要查找的pck文件所在文件夹地址（若目标pck文件在所输入文件夹的子文件夹下，则无法识别）：")
    if not os.path.exists(pck_dir_path):
        print("该pck文件不存在！\n")
        os.system("pause")
        exit()

    # 添加后缀
    if pck_dir_path[-1:] != '\\' and pck_dir_path[-1:] != '/':
        pck_dir_path += '\\'

    # 获取所有文件
    pck_list = os.listdir(pck_dir_path)

    wav_path = input("请输入进行查找的wav文件地址：")

    if not os.path.exists(wav_path):
        print("该wav文件不存在！\n")
        # os.system("pause")
        exit()

    wav_size = os.path.getsize(wav_path)

    with open(wav_path, "rb") as wav:
        for pck_name in pck_list:
            if pck_name[-4:] != '.pck':
                continue
            with open(pck_dir_path + pck_name, "rb") as pck:
                # 获取pck文件中包含的wav文件数量
                if is_computer:
                    pck.seek(0x00000038, 0)
                    pck_wav_num = hex_string_to_hex(pck.read(2))
                else:
                    pck.seek(0x00000034, 0)
                    pck_wav_num = hex_string_to_hex(pck.read(2))

                for pck_wav_index in range(1, pck_wav_num + 1):

                    # 判断文件大小是否相等
                    pck.seek(initial_offset + pck_wav_index * 24 - 24 + 13, 0)
                    pck_wav_size = hex_string_to_hex(pck.read(4))
                    if wav_size != pck_wav_size:
                        continue

                    # 比较两个 wav 文件内容是否相同
                    # 计算target_wav之前的数据大小
                    pck.seek(initial_offset + pck_wav_index * 24 - 24 + 17, 0)
                    target_wav_site = hex_string_to_hex(pck.read(4))
                    pck.seek(target_wav_site)

                    wav.seek(0)

                    # 比较 wav 文件内容
                    if wav.read(wav_size) == pck.read(pck_wav_size):
                        print('pck:{}\nwav编号:{}'.format(pck_name, pck_wav_index))
                        os.system('pause')
                        exit(0)

    print('未找到目标 wav 文件')
    os.system('pause')
