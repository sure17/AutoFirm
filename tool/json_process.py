import json



def get_dic(json_filename):
    """
    get dic from json
    :param json_filename:
    :return:
    """
    dic = {}
    with open(json_filename, 'r', encoding='UTF-8') as f:
        dic = json.load(f)
    return dic


def json_prefix(origin_json_file, fixed_json_file):
    """
    fix error json file and store it
    :param origin_json_file:
    :param fixed_json_file:
    :return:
    """
    fixed_txt = ""
    origin_txt = ""
    head = '{"file":['
    tail = '{}]}'
    with open(origin_json_file, 'r', encoding='UTF-8') as f:
        origin_txt = f.read()
        origin_txt = origin_txt.replace(']}', ']},')
        fixed_txt = head + origin_txt + tail
        with open(fixed_json_file, 'w') as ft:
            ft.write(fixed_txt)


def get_file_dic_list(json_file):
    """
    get info from fixed json file
    :param json_file:
    :return:
    """
    file_dic = get_dic(json_file)
    file_list = []
    for files in file_dic.values():
        for file in files:
            if len(file) != 0:
                file_list.append(file)

    return file_list
