import os
import shutil
import zipfile
import common
import tarfile
import rarfile


def inner_file(prefix):
    class NF:
        def __init__(self):
            self.file_path = ""
            self.file_size = ""

    discard_list = ['pdf', 'mib', 'txt', 'smi', 'xls', 'xlsx', 'svn-base', 'dat', 'doc', 'ppt', 'pptx', 'rft', 'docx',
                    'mht', 'png', 'jpg', 'svg', '.ds_store', 'rtf']

    file_list = []
    for relpath, dirs, files in os.walk(common.TARGET_DIR + prefix):
        for file in files:
            new_file = NF()
            if file.split('.')[-1].lower() in discard_list:
                continue
            new_file.file_path = os.path.join(relpath, file)
            new_file.file_size = os.stat(new_file.file_path).st_size
            file_list.append(new_file)
    file_list.sort(key=lambda x: x.file_size, reverse=True)
    final_file_path = file_list[0].file_path

    rmname_final_file_path = '/'.join(final_file_path.split('/')[:-1]) + '/' + final_file_path.split('/')[-1].replace(
        ' ', '_').replace('(', '_').replace(')', '_').replace('[', '_').replace(']', '_')
    os.rename(final_file_path, rmname_final_file_path)

    result_file_path = prefix + rmname_final_file_path.split('/')[-1]
    shutil.move(rmname_final_file_path, common.TARGET_DIR + result_file_path)

    return result_file_path


def unzip(file_path):
    prefix = file_path.split('.')[0]

    zp = zipfile.ZipFile(common.TARGET_DIR + file_path)
    for file in zp.namelist():
        zp.extract(file, common.TARGET_DIR + prefix)
    zp.close()

    return inner_file(prefix)


def untar(file_path):
    prefix = file_path.split('.')[0]

    tf = tarfile.open(common.TARGET_DIR + file_path)
    names = tf.getnames()
    for name in names:
        tf.extract(name, common.TARGET_DIR + prefix)
    tf.close()

    return inner_file(prefix)


def unrar(file_path):
    prefix = file_path.split('.')[0]

    rf = rarfile.RarFile(common.TARGET_DIR + file_path)
    rf.extractall(path=common.TARGET_DIR + prefix)
    rf.close()

    return inner_file(prefix)
