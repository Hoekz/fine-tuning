from src.codebase import code_from_repo, format_completion

if __name__ == "__main__":
  project = code_from_repo("./")

  print(format_completion("./main.py", ["./src/code.py", "./prompts/code-completion.md", "./prompts/code-file.md"], ["./requirements.txt"], project))
