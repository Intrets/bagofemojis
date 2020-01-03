def check_size(str: str, size):
    utf = str.encode('utf-8')
    return len(utf) <= size


def trim(str: str, size):
    utf = str.encode('utf-8')
    utf = utf[:size]
    return utf.decode('utf-8')
