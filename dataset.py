import sys
import random
from src.codebase import code_from_repo, format_completion
from src.types import CodeFile, CodeSnippet
from src.snippet import random_snippets

def important_project_file(path: str) -> bool:
  return path.endswith("package.json") or ".eslintrc" in path or "tsconfig" in path

def ignored_project_file(path: str) -> bool:
  return path.endswith("package-lock.json") or path.endswith(".svg") or path.endswith("README.md")

if __name__ == "__main__":
  project = code_from_repo(sys.argv[1])
  size = int(sys.argv[2])
  output = sys.argv[3]
  offset = int(sys.argv[4] if len(sys.argv) > 4 else 0)
  always_open_files = [f.path for f in project if important_project_file(f.path)]
  
  for i in range(size):
    current = random.choice([f for f in project if not important_project_file(f.path) and not ignored_project_file(f.path)])
    if (current.content.strip() == ""):
      continue
    amount_open = random.randint(0, 4)
    open_files = random.sample([f.path for f in project if f.path != current and not important_project_file(f.path) and not ignored_project_file(f.path)], amount_open)
    snippets = random_snippets(current.content, 1)
    use_project_structure = random.random() < 0.6
    end_of_file = random.random() < 0.3
    
    if end_of_file and snippets:
      saved = current.content
      current.content = current.content[:snippets[0].end]
      
    with open(f"{output}/sample-{i+1+offset:04}.md", "w") as f:
      if snippets:
        f.write(format_completion(current.path, open_files, always_open_files if use_project_structure else [], project, snippets[0]))
      else:
        f.write(format_completion(current.path, open_files, always_open_files if use_project_structure else [], project))

    if end_of_file and snippets:
      current.content = saved
