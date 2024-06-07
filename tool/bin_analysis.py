import json
import os
import time
import bin_process
import common
import path_search
import json_process
import decompress


def json_fix():
    """
    fix and preprocess json file
    it is the web scrawler problem, we will fix spider in the future
    :return:
    """
    print('\nFixing json...\n\n')
    json_process.json_prefix(common.ORIGIN_JSON_FILE, common.FIXED_JSON_FILE)
    file_dic_list = json_process.get_file_dic_list(common.FIXED_JSON_FILE)

    new_json = {'file': []}
    file_path_set = set()
    for file_dic in file_dic_list:
        file_path_list = file_dic['files']

        # get rid of fail download
        if len(file_path_list) != 0:
            # get rid of mib download
            if len(file_path_list) != 1:
                if 'mib' in file_dic.keys():
                    for i in range(len(file_path_list)):
                        if file_path_list[i]['url'] == file_dic['mib']:
                            file_dic['files'].pop(i)
                            break

            # some firmware does not have firmware name
            try:
                _ = file_dic['firmware_name']
            except BaseException:
                file_dic['firmware_name'] = file_dic['files'][0]['url'].split('/')[-1].strip()

            # deduplication download
            file_path = file_path_list[0]['path']
            if len(file_path_set) == 0:
                file_path_set.add(file_path)
            else:
                if file_path in file_path_set:
                    continue
                else:
                    file_path_set.add(file_path)

            new_json['file'].append(file_dic)
        else:
            pass

    with open(common.FIXED_JSON_FILE, 'w') as f:
        json.dump(new_json, f)


def json_fix2():
    """
    unzip zip, rar, tar and rewrite to json file
    :return:
    """
    print('\nUnzipping...\n\n')

    new_json = {'file': []}
    file_dic_list = json_process.get_file_dic_list(common.FIXED_JSON_FILE)
    for file_dic in file_dic_list:
        local_file_path = file_dic['files'][0]['path']  # vendor/xxx.xx
        local_file = local_file_path.split('/')[-1]  # xxx.xx

        print(local_file_path)

        if local_file.find('.') == -1:
            new_json['file'].append(file_dic)
            continue
        else:
            suffix = local_file.split('.')[-1].lower()

        try:
            if suffix == 'zip' or suffix == 'zhex':
                local_file = decompress.unzip(local_file)
            if suffix == 'rar':
                local_file = decompress.unrar(local_file)
            if suffix.find('tar') != -1 or suffix.find('gz') != -1:
                local_file = decompress.untar(local_file)
        except BaseException as err:
            print('\t' + str(err))
            new_json['file'].append(file_dic)
            continue

        file_dic['files'][0]['path'] = common.VENDOR + '/' + local_file
        new_json['file'].append(file_dic)

    with open(common.FIXED_JSON_FILE, 'w') as f:
        json.dump(new_json, f)


def prepare_analysis():
    """
    pre-analyze for special firmware and statistics
    :return:
    """
    start_time = time.time()
    print('\nPrepare analysising...\n\n')
    extraction_info2json = {}

    extracted_dir_list = os.listdir(common.TARGET_DIR)

    file_dic_list = json_process.get_file_dic_list(common.FIXED_JSON_FILE)
    for i, file_dic in enumerate(file_dic_list):
        extraction_info = {}

        local_file_path = file_dic['files'][0]['path']  # latter part: xxx/xxx
        print(local_file_path)
        local_file = local_file_path.split('/')[-1]

        firmware_name = file_dic['firmware_name']

        # interrupt protection
        new_fn = firmware_name + '-' + str(i)
        if common.VENDOR + '_extraction.json' in os.listdir('extract_jsons'):
            extraction_info2json = json_process.get_dic(common.EXTRACTION_JSON)
            if new_fn in extraction_info2json.keys():
                continue

        extraction_info['local_path'] = common.TARGET_DIR + local_file

        extract_dir = '_' + local_file + '.extracted'
        if extract_dir in extracted_dir_list:
            extraction_info['status'] = True

            bin_dir_list = path_search.search_bin_dir(common.TARGET_DIR + extract_dir)
            sbin_dir_list = path_search.search_sbin_dir(common.TARGET_DIR + extract_dir)
            if len(bin_dir_list) == 0 and len(sbin_dir_list) == 0:
                extraction_info['bins'] = None
                # None indicate that the firmware has 0 file or bin/sbin does not exist
            else:
                try:
                    arch = bin_process.get_arch(bin_dir_list)
                except BaseException as err:
                    print(err)
                    extraction_info['bins'] = None
                    # None indicate that the firmware has arch error. 
                    continue

                if len(arch) != 0:
                    extraction_info['arch'] = arch

                    bin_path_list = bin_process.get_bin_list(bin_dir_list)
                    sbin_path_list = bin_process.get_bin_list(sbin_dir_list)
                    total_bin_list = bin_path_list + sbin_path_list
                    if len(total_bin_list) == 0:
                        extraction_info['bins'] = None
                        # None indicate that the file command error
                    else:
                        extraction_info['bins'] = total_bin_list
                else:
                    extraction_info['bins'] = None
        else:
            extraction_info['status'] = False

        extraction_info2json[firmware_name + '-' + str(i)] = extraction_info
        with open(common.EXTRACTION_JSON, 'w') as f:
            json.dump(extraction_info2json, f)
        print('-' * 120)

    common.time_cnt(common.VENDOR, start_time)


def analysis():
    """
     emulate binary and get version info from it
    :return:
    """
    start_time = time.time()
    print('\nAnalysising...\n\n')

    def interrupt_protect(vendor, firmware_name):
        """
        write to log json file for interrupt protection
        :param vendor:
        :param firmware_name:
        :return:
        """
        if common.INTERRUPT_FILE not in os.listdir(common.LOG_PATH):
            new2json = {vendor: [firmware_name]}
            with open(common.INTERRUPT_LOG_JSON, 'w') as f:
                json.dump(new2json, f)
        else:
            runned_file_dic = json_process.get_dic(common.INTERRUPT_LOG_JSON)
            if vendor in runned_file_dic.keys():
                runned_file_dic[vendor].append(firmware_name)
            else:
                runned_file_dic[vendor] = [firmware_name]
            with open(common.INTERRUPT_LOG_JSON, 'w') as f:
                json.dump(runned_file_dic, f)

    file_dic = json_process.get_dic(common.EXTRACTION_JSON)

    runned_file_dic = {}
    if common.INTERRUPT_FILE in os.listdir(common.LOG_PATH):
        runned_file_dic = json_process.get_dic(common.INTERRUPT_LOG_JSON)

    for firmware_name, file_info_dic in file_dic.items():
        local_file = file_info_dic['local_path'].split('/')[-1]

        if common.VENDOR in runned_file_dic.keys() and firmware_name in runned_file_dic[common.VENDOR]:
            continue

        flag = file_info_dic['status']
        try:
            bins_list = file_info_dic['bins']
            arch = file_info_dic['arch']
        except KeyError:
            arch = None
            bins_list = None

        if flag and bins_list is not None \
                and arch is not None:
            print(firmware_name + '\n' + common.TARGET_DIR + local_file + ' start to analyze ...')

            bin_process.get_bin_ver(arch, bins_list, firmware_name)
        else:
            print(firmware_name + '\n' + common.TARGET_DIR + local_file + ' fail to analyze ...')

        interrupt_protect(common.VENDOR, firmware_name)
        print('-' * 120)

    common.time_cnt(common.VENDOR, start_time)
