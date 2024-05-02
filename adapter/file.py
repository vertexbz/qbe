from __future__ import annotations


def writefile(path: str, data: str) -> int:
    with open(path, 'w', encoding='utf-8') as stream:
        return stream.write(data)


def readfile(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as stream:
        return stream.read()
