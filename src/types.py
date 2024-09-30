class CodeFile:
    def __init__(self, path: str, content: str) -> None:
        self.path = path
        self.content = content

    def __repr__(self) -> str:
        return f'{{"path":"{self.path}","content":"{self.content}"}}'

    def __str__(self) -> str:
        return f'{{"path":"{self.path}","content":"{self.content}"}}'

class CodeSnippet:
    def __init__(self, start: int, end: int, type: str = "inline") -> None:
        self.start = start
        self.end = end
        self.type = type

    def __repr__(self) -> str:
        return f'{{"type":"{self.type}","start":{self.start},"end":{self.end}}}'

    def __str__(self) -> str:
        return f'{{"type":"{self.type}","start":{self.start},"end":{self.end}}}'