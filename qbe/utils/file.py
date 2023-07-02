def writefile(path: str, data: str) -> None:
    with open(path, 'w', encoding='utf-8') as stream:
        stream.write(data)


def readfile(path: str) -> str:
    with open(path, encoding='utf8') as f:
        return f.read()
