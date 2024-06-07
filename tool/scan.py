import json
import os
import common
import linux_shell
import json_process


def scan2json():
    """
    scan firmware head and write to json
    :return:
    """
    print('\nFirmware scaning...\n\n')
    scan_info2json = {}

    file_dic_list = json_process.get_file_dic_list(common.FIXED_JSON_FILE)
    for i, file_dic in enumerate(file_dic_list):
        local_file_path = file_dic['files'][0]['path']  # latter part: xxx/xxx
        print(local_file_path)
        local_file = local_file_path.split('/')[-1]

        firmware_name = file_dic['firmware_name']

        # interrupt protection
        new_fn = firmware_name + '-' + str(i)
        if common.VENDOR + '_scan.json' in os.listdir('scan_result'):
            scan_info2json = json_process.get_dic('scan_result/' + common.VENDOR + '_scan.json')
            if new_fn in scan_info2json.keys():
                continue

        _, result_list = linux_shell.binwalk_scan(common.TARGET_DIR, local_file)
        scan_info2json[firmware_name] = result_list
        
        with open('scan_result/' + common.VENDOR + '_scan.json', 'w') as f:
            json.dump(scan_info2json, f)
