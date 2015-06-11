import ast
from operator import itemgetter
from astor import to_source


CLASS_ROOT_NAME = '[CN]'
CONSTRUCTOR_ROOT_NAME = '[CS]'
METHOD_ROOT_NAME = '[MT]'

BODY_BLOB = 'body'
PARAMETERS_BLOB = 'parameters'
EXTEND_BLOB = 'extend'
OTHER_BLOB = 'other'


def get_blob(name, text):
    lines = ['[BN] {}'.format(name),
             '[BI] {}'.format(len(text))]
    lines.extend(text)
    return lines


def get_tree(name, contents):
    lines = []
    lines.append('[TS] {}'.format(name))
    contents = sorted(contents, key=itemgetter(1))
    for t, n, c in contents:
        if t == 'blob':
            lines.extend(get_blob(n, c))
        elif t == 'tree':
            lines.extend(get_tree(n, c))
    lines.append('[TE] {}'.format(name))
    return lines


def create_class_tree(class_def):
    inner_class_defs = []
    func_defs = []
    constructor_defs = []
    for child in class_def.body:
        if isinstance(child, ast.ClassDef):
            inner_class_defs.append(child)
        elif isinstance(child, ast.FunctionDef):
            if is_constructor(child):
                constructor_defs.append(child)
            else:
                func_defs.append(child)

    contents = []

    inner_class_contents = []
    for inner_class_def in inner_class_defs:
        inner_class_contents.append(create_class_tree(inner_class_def))
    if inner_class_contents:
        contents.append(('tree', CLASS_ROOT_NAME, inner_class_contents))

    constructor_contents = []
    for constructor_def in constructor_defs:
        constructor_contents.append(create_func_tree(constructor_def))
    if constructor_contents:
        contents.append(('tree', CONSTRUCTOR_ROOT_NAME, constructor_contents))

    function_contents = []
    for func_def in func_defs:
        function_contents.append(create_func_tree(func_def))
    if function_contents:
        contents.append(('tree', METHOD_ROOT_NAME, function_contents))

    assert hasattr(class_def, 'bases')
    if class_def.bases:
        bases = []
        for base in class_def.bases:
            bases.append(to_source(base))
        contents.append(('blob', EXTEND_BLOB, bases))

    return ('tree', class_def.name, contents)


def create_func_tree(node):
    src = to_source(node).split('\n')

    function_name = node.name

    contents = []
    contents.append(('blob', BODY_BLOB, src))

    args = []
    for arg in node.args.args:
        if isinstance(arg, ast.Name):
            args.append(arg.id)
        else:
            args.append(to_source(arg))
    contents.append(('blob', PARAMETERS_BLOB, args))

    return ('tree', function_name, contents)


def is_constructor(node):
    return node.name == '__new__' or node.name == '__init__'


def parse_and_write_gittree(src, dst_path):
    try:
        ast_root = ast.parse(src)
    except Exception:
        ast_root = []

    with open(dst_path, 'w') as output_file:
        lines = create_tree(ast_root)

        output_file.write('\n'.join(lines))
        output_file.write('\n')


def create_tree(node):
    lines = []
    assert hasattr(node, 'body')

    func_contents = []
    class_contents = []
    others = []
    for child in node.body:
        if isinstance(child, ast.ClassDef):
            class_contents.append(create_class_tree(child))
        elif isinstance(child, ast.FunctionDef):
            func_contents.append(create_func_tree(child))
        else:
            others.append(child)

    lines.extend(get_tree(METHOD_ROOT_NAME, func_contents))
    lines.extend(get_tree(CLASS_ROOT_NAME, class_contents))

    # write others
    if others:
        src = '\n'.join(map(to_source, others)).split('\n')
        lines.extend(get_blob(OTHER_BLOB, src))

    return lines


def main():
    import sys
    if len(sys.argv) != 2:
        print('usage : python {} <absolute path of output file>'.format(sys.argv[0]))
        return

    src = sys.stdin.read()
    parse_and_write_gittree(src, sys.argv[1])

if __name__ == '__main__':
    main()
