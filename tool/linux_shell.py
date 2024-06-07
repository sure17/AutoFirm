# coding=UTF-8
import csv
import os
import re
import subprocess
from multiprocessing import Manager, Pool
import common


def csv2dic(path):
    _dic = {}
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            tmp = line.strip().split(',')
            _dic[tmp[0]] = tmp[1]
    return _dic


def extract_file(path):
    """
    use binwalk to extract firmware system in 60 seconds
    """
    command = 'binwalk -Me %s' % path

    res = subprocess.Popen(
        command,
        shell=True,
        cwd=common.TARGET_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    try:
        _, _ = res.communicate(timeout=20)
        return True
    except subprocess.TimeoutExpired as err:
        os.killpg(os.getpgid(res.pid), 9)
        res.kill()
        print('extract error:', str(err))
        return False


def judge_elf(path, file_name):
    """
    use linux file command to get info from binary
    """
    cwd = path
    command = "file %s" % file_name
    res = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    right = str(res.stdout.read(), encoding="utf-8")
    if right.find('ELF') != -1:
        return right, True
    else:
        return '', False


def binwalk_scan(root_path, file_path):
    """
    use binwalk -B scan filesystem
    """
    command = "binwalk -B %s" % file_path

    res = subprocess.Popen(
        command,
        shell=True,
        cwd=root_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    try:
        stdout_data, stderr_data = res.communicate(timeout=30)
        # stdout_data, stderr_data = subprocess.Popen(
        #     command,
        #     shell=True,
        #     cwd=root_path,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT
        # ).communicate(timeout=30)
        result_list = str(stdout_data, 'iso-8859-1').strip().split('\n')
        return True, result_list
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(res.pid), 9)
        res.kill()
        return False, None


def get_elf_arch(bin_dir):
    """
    use linux file command to get architecture info from binary
    :param bin_dir:
    :return:
    """
    for file in os.listdir(bin_dir):
        if os.path.isfile(os.path.join(bin_dir, file)):
            result, flag = judge_elf(bin_dir, file)
            if flag:
                return result
    return ''  # no ELF in bin list


def str_process(result_str):
    """
    emulation excel_result clear
    :param result_str:
    :return:
    """
    result_list = []
    clear_str = ['(', ')', ':', '/', ',', '\t', '$', ]

    result_str_list = result_str.split('\n')
    for str in result_str_list:
        if len(str) != 0:
            str = str.strip().lower()
            for cs in clear_str:
                str = str.replace(cs, ' ')

            flag = False
            for s in str.strip():
                if s.isdigit():
                    flag = True
                    break
            if flag:
                result_list.append(str)

    return result_list


def qemu_shell(share_list, command, cwd, lock):
    """
    sub process
    :param share_list:
    :param command:
    :param cwd:
    :param lock:
    :return:
    """

    env_dic = {'QEMU_LD_PREFIX': './'}

    result_str = ""
    res = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        env=env_dic,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    try:
        stdout_data, stderr_data = res.communicate(timeout=10)
        s = str(stdout_data, 'iso-8859-1')

        result_list = str_process(s)
        with lock:
            share_list += result_list
            with open(common.ORIGIN_QEMU_OUT, 'a', encoding='iso-8859-1') as f:
                f.write('-' * 120 + '\n$' + command + '\n' + s + '\n' + '-' * 120)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(res.pid), 9)
        res.kill()
        pass


def qemu_emulation(qemu_command, root_path, bin_dir):
    """
    use qemu to emulate binary
    :param qemu_command:
    :param root_path:
    :param bin_dir:
    :return:
    """
    cwd = root_path

    common_command = qemu_command + " " + bin_dir

    bin_name = bin_dir.split('/')[-1].strip().lower()
    special_command_dic = csv2dic(common.SPECIAL_COMMAND)
    if bin_name in special_command_dic.keys():  # for special binary
        common_command += ' ' + special_command_dic[bin_name]

    command_list = [
        common_command + ' --version',
        common_command + ' -V',
        common_command + ' -v',
        common_command + ' --help',
        common_command + ' -H',
        common_command + ' -h',
        common_command,
    ]

    manager = Manager()
    lock = manager.Lock()
    share_list = manager.list()
    msgs = []
    for command in command_list:
        msgs.append((share_list, command, cwd, lock))
    pool = Pool(10)
    pool.starmap(qemu_shell, msgs)
    pool.close()
    pool.join()

    result_set = set(share_list)
    result_str = '\n'.join(list(result_set))
    if len(result_str) == 0:
        result_str = 'None'

    # common_regex = r'(\d{1,4}(?:\.\d{1,4}){0,3})'
    # common_regex = r'((0|[1-9]\d{0,3})(?:\.\d{1,2}){1,2}([a-z])?)'
    common_regex = r'((0|[1-9]\d{0,3})(?:\.\d{1,2}){1,2}([a-z])?(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?)'
    pre_regex = r'[a-z\s\-\_\.]*'

    special_ver_dic = csv2dic(common.SPECIAL_VER)
    special_regex = [i[0] for i in list(csv.reader(open(common.SPECIAL_REGEX, 'r')))]

    if bin_name in special_regex:
        regex = common_regex
    elif bin_name in special_ver_dic.keys():
        regex = re.escape(special_ver_dic[bin_name]) + pre_regex + common_regex
    else:
        regex = re.escape(bin_name) + pre_regex + common_regex

    ver_set = set()
    for value in result_set:
        for i in re.findall(regex, value):
            ver_set.add(i)

    return ver_set, result_str
