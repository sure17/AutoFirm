import os
import linux_shell
import json_process
import common
import pandas as pd
import logging
import csv

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

handler = logging.FileHandler(common.RUN_LOG, 'a')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_arch(bin_dir_list):
    """
    get bin arch by read head
    :param bin_dir_list:
    :return:
    """
    result = ''
    for bin_dir in bin_dir_list:
        s = linux_shell.get_elf_arch(bin_dir).strip()
        if len(s) != 0:
            print('\t' + bin_dir + '\n\t' + s)
            result = s
            break

    arch = ''.join(result.split(',')[1:3]).strip()
    if result.find('MSB') != -1:
        arch += ' MSB'
    elif result.find('LSB') != -1:
        arch += ' LSB'
    return arch


def get_bin_list(path_list):
    """
    :param path_list:
    :return:
    """
    bin_path_list = []
    for path in path_list:
        for relpath, dirs, files in os.walk(path):
            for file in files:
                _, flag = linux_shell.judge_elf(path, file)
                if flag:
                    bin_path_list.append(os.path.join(relpath, file))
    return bin_path_list


def to_excel(bin_ver_dic, firmware_name):
    """
    write to excel and mainly for interrupt protection
    :param bin_ver_dic:
    :param firmware_name:
    :return:
    """
    if common.EXCEL_FILENAME in os.listdir(common.EXCEL_FILE_PATH):
        new_col = pd.Series(data=bin_ver_dic, name=firmware_name, dtype='object')
        new_df = pd.DataFrame(new_col)

        old_df = pd.read_excel(common.EXCEL, index_col=0)

        s = pd.concat([old_df, new_df], axis=1, join='outer')
        s.to_excel(common.EXCEL)
    else:
        new_col = pd.Series(data=bin_ver_dic, name=firmware_name, dtype='object')
        s = pd.DataFrame(new_col)
        s.to_excel(common.EXCEL)


def find_root_path(bin_path):
    """
    set emulation root path, by qemu user mode documentation
    :param bin_path:
    :return:
    """
    cut_flag = -2
    dir_split_list = bin_path.split('/')
    for i in range(8, len(dir_split_list)):
        if 'bin' and 'sbin' in os.listdir('/'.join(bin_path.split('/')[:i])):
            cut_flag = i
            break
    return cut_flag


def ver_emu_result(qemu_command, bin_path, root_path, bin_dir):
    """

    :param qemu_command:
    :param bin_path:
    :param root_path:
    :param bin_dir:
    :return:
    """

    ver_set, result_str = linux_shell.qemu_emulation(qemu_command, root_path, bin_dir)
    with open(common.QEMU_LOG, 'a') as f:
        f.write('*' * 120 + '\n' + bin_path + '\n' + result_str + '\n')

    result = '|'.join(list(ver_set))
    if len(result) == 0:
        result = '|None'
    return result


def get_bin_ver(arch, bins_list, firmware_name):
    """
    get binary version info by qemu emulation
    :param arch:
    :param bins_list:
    :param firmware_name:
    :return:
    """

    arch_dic = json_process.get_dic(common.ARCH_JSON)
    try:
        qemu_command = arch_dic[arch]
    except:
        return

    if len(qemu_command) == 0:
        print('emulation fail : lack arch')
        return

    with open(common.QEMU_LOG, 'a') as f:  # log start line
        f.write('-Start' * 20 + '\n-' + firmware_name + ' start to analyze ...\n')

    cut_flag = find_root_path(bins_list[0])

    bin_ver_dic = {}
    for i in range(len(bins_list)):
        bin_path = bins_list[i]
        logger.info(bin_path)

        # emulation root path,
        # eg:/media/xxx/ElementsSE/output/360/_fa687831e08a53600bcdb1369d9e5789605bf23d.bin.extracted/squashfs-root
        root_path = '/'.join(bin_path.split('/')[:cut_flag])
        # eg:./bin/busybox
        bin_dir = './' + '/'.join(bin_path.split('/')[cut_flag:])
        print('\t', root_path, '\n\t\t', bin_dir)
        logger.info(root_path + '::' + bin_dir)

        flag = False
        bin_name = bin_dir.split('/')[-1].lower()

        black_list = [i[0] for i in list(csv.reader(open(common.BLACK_LIST, 'r')))]
        for black_sheep in black_list:
            if bin_name.find(black_sheep) != -1:
                flag = True
                break
        if flag:
            continue

        if bin_name not in bin_ver_dic.keys():
            bin_ver_dic[bin_name] = ver_emu_result(qemu_command, bin_path, root_path, bin_dir)
        else:
            bin_ver_dic[bin_name] += ver_emu_result(qemu_command, bin_path, root_path, bin_dir)

    to_excel(bin_ver_dic, firmware_name)

    with open(common.QEMU_LOG, 'a') as f:  # log end line
        f.write('-End' * 30 + '\n')
