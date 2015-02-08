from factories import *
from context import root
from codegen import to_source

context = root()
a = new_while_loop(context)
astr = to_source(a, indent_with='\t')
print astr
with open('generated.py', 'w') as file:
    file.write(astr)