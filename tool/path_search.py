import os


def search_dir(path, target_dir):
    """
    search binary dir from path
    :param path:
    :param target_dir:
    :return:
    """
    result_path_list = []
    for relpath, dirs, files in os.walk(path):
        for dir in dirs:  # all of them
            if target_dir == dir:
                result_path_list.append(os.path.join(relpath, dir))
    return result_path_list


def search_bin_dir(path):
    """
    search /bin dir
    :param path:
    :return:
    """

    return search_dir(path, 'bin')


def search_sbin_dir(path):
    """
    search /sin dir
    :param path:
    :return:
    """
    return search_dir(path, 'sbin')
