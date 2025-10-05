
def readFile(path: str) -> str:
    apiFile = open(path, "r", encoding="UTF-8")
    data = apiFile.read()
    apiFile.close()
    return data
