import os
import time
import common
import json_process
import linux_shell


EXTRACT_TIMEOUT = 5


def extract_check(subdir):
    """
    for low speed of external disk
    :param subdir:
    :return:
    """
    start_time = time.time()
    while True:
        end_time = time.time()
        try:
            if os.listdir(common.TARGET_DIR + subdir) != 0:
                break
            elif end_time - start_time > EXTRACT_TIMEOUT:
                break
            else:
                print('.', end='')
                time.sleep(1)
        except BaseException as err:
            if end_time - start_time > EXTRACT_TIMEOUT:
                break
            print('.', end='')
            time.sleep(1)
    print('\tdone')


def extract_filesystem():
    """
    use binwalk to extract filesystem under the vendor path
    design for a single function because of the low speed of usb external disks
    :return:
    """
    start_time = time.time()

    print('\nExtracting...\n\n')
    extracted_dir_list = os.listdir(common.TARGET_DIR)

    file_dic_list = json_process.get_file_dic_list(common.FIXED_JSON_FILE)
    for file_dic in file_dic_list:
        local_file_path = file_dic['files'][0]['path']
        print(local_file_path)

        local_file = local_file_path.split('/')[-1]  # xxx.bin
        subdir = '_' + local_file + '.extracted'

        if subdir not in extracted_dir_list:
            if not linux_shell.extract_file(common.TARGET_DIR + local_file):
                continue
            extract_check(subdir)

    common.time_cnt(common.VENDOR, start_time)
