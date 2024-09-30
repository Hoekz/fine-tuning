from typing import List, Tuple, Dict, Any, Optional
import random
from src.types import CodeSnippet

def indent(code: str) -> int:
  return len(code) - len(code.lstrip())

def next_space(code: str, start: int) -> int:
  for i in range(start, len(code)):
    if code[i] == " " or code[i] == "\n" or code[i] == "\t":
      return start + i
  return len(code)

def next_non_space(code: str, start: int) -> int:
  for i in range(start, len(code)):
    if code[i] != " " and code[i] != "\n" and code[i] != "\t":
      return start + i
  return len(code)

tokens = ["\"", "'", "`", "(", ")", "[", "]", "{", "}", ";", ":", ",", ".", "?", "!", " ", "\t", "\n"]

def next_token(code: str, start: int) -> int:
  for i in range(start, len(code)):
    if code[i] in tokens:
      return start + i
  return len(code)

def prev_token(code: str, start: int) -> int:
  for i in range(start, -1, -1):
    if code[i] in tokens:
      return i
  return start

def random_inline_completion(code: str) -> Optional[CodeSnippet]:
  lines = code.split("\n")
  line = random.randint(0, len(lines) - 1)
  attempts = 1
  while lines[line].strip() == "":
    attempts += 1
    if attempts > 10:
      return None
    line = random.randint(0, len(lines) - 1)
  start = random.randint(0, len(lines[line]) - 1)
  end = min(random.randint(start, int(len(lines[line]) * 1.25)), len(lines[line]))
  real_start = prev_token(lines[line], start)
  real_end = next_token(lines[line], end)
  offset = len("\n".join(lines[:line]))
  return CodeSnippet(offset + real_start, offset + real_end, "inline")

def random_line_snippet(code: str, min_lines: int, max_lines: int) -> CodeSnippet:
  lines = code.split("\n")
  size = random.randint(min_lines, min(max_lines, len(lines) - 1))
  start = random.randint(0, max(len(lines) - size, 1))
  while lines[start].strip() == "":
    start = random.randint(0, max(len(lines) - size, 1))
  
  if indent(lines[start + 1]) > indent(lines[start]):
    block_end = start + 1
    while block_end - start < max_lines and indent(lines[block_end]) > indent(lines[start]):
      block_end += 1
    
    if block_end - start < size:
      return CodeSnippet(len("\n".join(lines[:start])), len("\n".join(lines[start:block_end])), "multiline")
    
  return CodeSnippet(len("\n".join(lines[:start-1])), len("\n".join(lines[:start+size])), "multiline")

scopes = [("{", "}"), ("[", "]"), ("(", ")"), ("<", ">"), ("'''", "'''"), ('"""', '"""'), ("/*", "*/")]

def random_scoped_snippet(code: str, splitters: List[Tuple[str, str]] = scopes) -> Optional[CodeSnippet]:
  if not splitters:
    return None

  (open, close) = random.choice(splitters)
  if not open in code:
    return random_scoped_snippet(code, [scope for scope in splitters if scope != (open, close)])

  stack = [open]
  choices = [i for i in range(len(code)) if code[i:i+len(open)] == open]
  start = random.choice(choices)
  real_start = random.choice([
    start,
    code[:start].rfind('\n') + 1,
    code[:start].rfind(' '),
    code[:start].rfind(' ') + 1,
    next_non_space(code, start)
  ])

  for i in range(start + 1, len(code)):
    if code[i] == close and code[i-1] != "\\":
      if len(stack) == 1:
        return CodeSnippet(real_start,i+1, f"scoped: {open}{close}")
      else:
        stack.pop()
    elif code[i] == open and open != close and code[i-1] != "\\":
      stack.append(open)
  
  return CodeSnippet(real_start, len(code), f"scoped (no close): {open}{close}")

def random_string_snippet(code: str) -> CodeSnippet:
  quotes = ["'", '"', "`"]

  starts = []
  ends = []
  active = None
  for i in range(len(code)):
    if code[i] in quotes and not active:
      starts.append(i)
      active = code[i]
    elif code[i] == quote and quote == active and code[i - 1] != "\\":
      ends.append(i)
      active = None

  quote = random.randint(0, len(starts))
  return CodeSnippet(starts[quote], ends[quote] + 1, "string")
  

default_options = {
  "min_lines": 1,
  "max_lines": 10,
  "splitters": scopes,
  "inline_probability": 0.1,
  "multi_line_probability": 0.4,
  "string_probability": 0.1,
  "scope_probability": 0.4,
}

def random_snippets(code: str, amount: int, options: Dict[str, Any] = {}) -> List[CodeSnippet]:
  min_lines = options.get("min_lines", default_options["min_lines"])
  max_lines = options.get("max_lines", default_options["max_lines"])
  splitters = options.get("splitters", default_options["splitters"])
  inline_probability = options.get("inline_probability", default_options["inline_probability"])
  multi_line_probability = options.get("multi_line_probability", default_options["multi_line_probability"])
  string_probability = options.get("string_probability", default_options["string_probability"])
  scope_probability = options.get("scope_probability", default_options["scope_probability"])
  
  snippets = []
  while len(snippets) < amount:
    try:
      choice = random.random() - inline_probability
      if choice < 0:
        snippet = random_inline_completion(code)
      else:
        choice -= multi_line_probability
        if choice < 0:
          snippet = random_line_snippet(code, min_lines, max_lines)
        else:
          choice -= string_probability
          if choice < 0:
            snippet = random_string_snippet(code)
          else:
            snippet = random_scoped_snippet(code, splitters)
      
      if snippet and code[snippet.start:snippet.end].strip() != "":
        snippets.append(snippet)
    except Exception as e:
      pass

  return snippets
