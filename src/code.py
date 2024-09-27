from typing import List
import os
import re

class CodeFile:
    def __init__(self, path: str, content: str) -> None:
        self.path = path
        self.content = content

    def __repr__(self) -> str:
        return f'{{"path":"{self.path}","content":"{self.content}"}}'

    def __str__(self) -> str:
        return f'{{"path":"{self.path}","content":"{self.content}"}}'

def code_from_repo(path: str) -> List[CodeFile]:
    code = []
    ignored = [glob_to_regex(".git")]
    with open(os.path.join(path, ".gitignore"), "r", encoding="utf-8") as f:
        ignored += [glob_to_regex(line.strip()) for line in f.readlines() if line.strip() != ""]

    for root, dirs, files in os.walk(path):
        for file in files:
            if not ignore_file(os.path.join(root, file), ignored):
                with open(os.path.join(root, file), "r") as f:
                    code.append(CodeFile(os.path.join(root, file), f.read()))
    return code

def glob_to_regex(glob: str) -> re.Pattern:
    return re.compile(glob.replace(".", "\\.").replace("*", ".*").replace("?", "."))

def ignore_file(file: str, ignored: List[re.Pattern]) -> bool:
    for pattern in ignored:
        if pattern.search(file):
            return True
    return False

def format_code_file(code_file: CodeFile) -> str:
    with open("./prompts/code-file.md", "r") as f:
        prompt = f.read()
        lang = lang_from_filename(code_file.path)
        
        if lang == "md":
            return prompt.replace("```", "````").format(filename=code_file.path, language="md", code=code_file.content)

        return prompt.format(filename=code_file.path, language=lang_from_filename(code_file.path), code=code_file.content)

def lang_from_filename(filename: str):
    return filename.split(".")[-1]

def format_completion(current: str, open_files: List[str], always_open_files: List[str], files: List[CodeFile]) -> str:
    lookup = { f.path: f for f in files }

    with open("./prompts/code-completion.md", "r") as f:
        prompt = f.read()
        project_structure = format_project_structure([f.path for f in files])
        project_files = "\n\n".join([format_code_file(lookup[f]) for f in always_open_files])
        editor_files = "\n\n".join([format_code_file(lookup[f]) for f in open_files])
        current_file = format_code_file(lookup[current])
        
        return prompt.format(current_file=current_file, project_structure=project_structure, project_files=project_files, editor_files=editor_files)

class File:
    def __init__(self, path: str) -> None:
        self.path = path

class Folder(File):
    def __init__(self, path: str, files: List[File]) -> None:
        self.path = path
        self.files = files
    
    def add_file(self, file: str) -> File:
        self.files.append(File(file))
        return self.files[-1]

    def add_folder(self, folder: str) -> 'Folder':
        for f in self.files:
            if f.path == folder and isinstance(f, Folder):
                return f

        f = Folder(folder, [])
        self.files.append(f)
        return f
            

def encode_tree(tree: Folder, prefix = "") -> str:
    node = prefix + "├── {}\n"
    last = prefix + "└── {}\n"
    printed_tree = ""
    
    for i, f in enumerate(tree.files):
        if i == len(tree.files) - 1:
            printed_tree += last.format(f.path)
        else:
            printed_tree += node.format(f.path)
        
        if isinstance(f, Folder):
            printed_tree += encode_tree(f, prefix + "    " if i == len(tree.files) - 1 else prefix + "|   ")
    
    return printed_tree

def format_project_structure(files: List[str]) -> str:    
    paths = [f.strip().replace("./", "").split(os.sep) for f in sorted(files)]
    
    tree = Folder("", [])
    
    for i, path in enumerate(paths):
        current = tree
        for j, part in enumerate(path):
            if j == len(path) - 1:
                current.add_file(part)
            else:
                current = current.add_folder(part)
    
    return encode_tree(tree)
    