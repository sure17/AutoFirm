import time
import sys

VENDOR = '360'
# VENDOR = 'asus'
# VENDOR = 'buffalo'
# VENDOR = 'dlink'
# VENDOR = 'foscam'
# VENDOR = 'mercury'
# VENDOR = 'microstrain'
# VENDOR = 'mikrotik'
# VENDOR = 'netgear'
# VENDOR = 'qnap'
# VENDOR = 'se'
# VENDOR = 'supermicro'
# VENDOR = 'synology'
# VENDOR = 'tenda'
# VENDOR = 'ti'
# VENDOR = 'tomato-shibby'
# VENDOR = 'tp-link'
# VENDOR = 'trendnet'
# VENDOR = 'ubiquiti'
# VENDOR = 'xerox'

# none file
# VENDOR = 'linksys'
# VENDOR = 'openwrt'


FIRMWARE_DIR = '/media/lnzb/lnzb/output/'
TARGET_DIR = FIRMWARE_DIR + VENDOR + '/'

ORIGIN_JSON_FILE = TARGET_DIR + VENDOR + '_download.json'
FIXED_JSON_FILE = TARGET_DIR + VENDOR + '.json'

JSON_PATH = 'extract_jsons/'

EXTRACTION_JSON = JSON_PATH + VENDOR + '_extraction.json'

EXCEL_FILE_PATH = 'excel_result/'
EXCEL_FILENAME = VENDOR + '.xlsx'
EXCEL = EXCEL_FILE_PATH + EXCEL_FILENAME

QEMU_LOG_PATH = './qemu_log/'
QEMU_LOG_FILENAME = VENDOR + '_qemu_log'
QEMU_LOG = QEMU_LOG_PATH + QEMU_LOG_FILENAME

ORIGIN_QEMU_OUT_PATH = './origin_qemu_output/'
ORIGIN_QEMU_OUT_FILENAME = VENDOR + '_qemu_out'
ORIGIN_QEMU_OUT = ORIGIN_QEMU_OUT_PATH + ORIGIN_QEMU_OUT_FILENAME

LOG_PATH = './log/'

LOG_FILE = VENDOR + '_run_log'
RUN_LOG = LOG_PATH + LOG_FILE

INTERRUPT_FILE = 'log.json'
INTERRUPT_LOG_JSON = LOG_PATH + INTERRUPT_FILE

# break down when emulation
EMU_TXT = 'emulation_txt/'
BLACK_LIST = EMU_TXT + 'black_list.csv'
ARCH_JSON = EMU_TXT + 'arch.json'
SPECIAL_VER = EMU_TXT + 'special_ver.csv'
SPECIAL_REGEX = EMU_TXT + 'special_regex.csv'
SPECIAL_COMMAND = EMU_TXT + 'special_command.csv'


def time_cnt(vendor, start_time):
    """
    Record function runtime and write to time/vendor.txt
    :param vendor:
    :param start_time:
    :return:
    """
    t = time.time() - start_time
    with open('time/' + vendor + '.txt', 'a') as f:
        f.write('%s-%s:%d:%d:%d\n' % (vendor, sys._getframe().f_code.co_name, t / 3600, t % 3600 / 60, t % 3600 % 60))
