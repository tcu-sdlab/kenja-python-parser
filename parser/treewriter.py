import ast
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
    for t, n, c in contents:
        if t == 'blob':
            lines.extend(get_blob(n, c))
        elif t == 'tree':
            lines.extend(get_tree(n, c))
    lines.append('[TE] {}'.format(name))
    return lines


class TreeWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.contents = []

    def write_tree(self, node):
        self.create_tree(node)

        self.output_file.write('\n'.join(self.contents))
        self.output_file.write('\n')

    def create_tree(self, node):
        assert hasattr(node, 'body')

        func_contents = []
        class_contents = []
        others = []
        for child in node.body:
            if isinstance(child, ast.ClassDef):
                class_contents.append(self.create_func_tree(child))
            elif isinstance(child, ast.FunctionDef):
                func_contents.append(self.create_class_tree(child))
            else:
                others.append(child)

        self.contents.extend(get_tree(METHOD_ROOT_NAME, func_contents))
        self.contents.extend(get_tree(CLASS_ROOT_NAME, class_contents))

        # write others
        if others:
            self.create_other_tree(others)

    def create_class_tree(self, class_def):
        inner_class_defs = []
        func_defs = []
        constructor_defs = []
        for child in class_def.body:
            if isinstance(child, ast.ClassDef):
                inner_class_defs.append(child)
            elif isinstance(child, ast.FunctionDef):
                if self.is_constructor(child):
                    constructor_defs.append(child)
                else:
                    func_defs.append(child)

        contents = []

        inner_class_contents = []
        for inner_class_def in inner_class_defs:
            inner_class_contents.extend(self.create_class_tree(inner_class_def))
        if inner_class_contents:
            contents.append(('tree', CLASS_ROOT_NAME, inner_class_contents))

        constructor_contents = []
        for constructor_def in constructor_defs:
            constructor_contents.append(self.create_func_tree(constructor_def))
        if constructor_contents:
            contents.append(('tree', CONSTRUCTOR_ROOT_NAME, constructor_contents))

        function_contents = []
        for func_def in func_defs:
            function_contents.append(self.create_func_tree(func_def))
        if function_contents:
            contents.append(('tree', METHOD_ROOT_NAME, function_contents))

        assert hasattr(class_def, 'bases')
        if class_def.bases:
            src = to_source(class_def.bases)
            contents.append(('blob', EXTEND_BLOB, src))

        return ('tree', class_def.name, contents)

    def create_func_tree(self, node):
        src = to_source(node).split('\n')

        # src[0] has def foobar(...):
        # src[4:-1] means foobar(...)
        assert src[0].startswith('def ')
        assert src[0][-1] == ':'
        function_name = src.pop(0)[4:-1]

        contents = []
        contents.append(('blob', BODY_BLOB, src))

        args = [args.id for args in node.args.args]
        contents.append(('blob', PARAMETERS_BLOB, args))

        return ('tree', function_name, contents)

    def create_other_tree(self, node):
        src = '\n'.join(map(to_source, node)).split('\n')
        self.contents.extend(get_blob(OTHER_BLOB, src))

    def is_constructor(self, node):
        return node.name == '__new__' or node.name == '__init__'
