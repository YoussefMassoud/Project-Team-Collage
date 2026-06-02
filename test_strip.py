import tokenize
import io

path = "D:\\youssef2\\Project-Team-Collage\\backend\\AllFlow\\app.py"

with open(path, "r", encoding="utf-8") as f:
    source = f.read()

tokens = tokenize.generate_tokens(io.StringIO(source).readline)

result = []
prev_token = None

for tok in tokens:
    tok_type, tok_str, start, end, line = tok
    
    if tok_type == tokenize.COMMENT:
        continue
    
    if tok_type == tokenize.STRING and tok_str.startswith(('"""', "'''")):
        if prev_token is None or prev_token[0] in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.NL):
            continue
    
    result.append(tok_str if tok_type != tokenize.NL else "")
    prev_token = tok

output = "".join(result)
print(output)
