import ast
from astor import to_source


TREE = '[TN] '
START_TREE = '[TS] '
END_TREE = '[TE] '

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

class TreeWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.contents = []

    def write_tree(self, node):
        self.create_tree(node)
        self.write_file()

    def create_tree(self, node):
        class_defs = []
        func_defs = []
        others = []

        if not hasattr(node, 'body'):
            return

        for child in node.body:
            if isinstance(child, ast.ClassDef):
                class_defs.append(child)
            elif isinstance(child, ast.FunctionDef):
                func_defs.append(child)
            else:
                others.append(child)

        # write func
        constructor_tmp = []
        func_tmp = []
        for node_func in func_defs:
            if self.is_constructor(node_func):
                constructor_tmp.append(node_func)
            else:
                func_tmp.append(node_func)

        if constructor_tmp:
            self.contents.append(START_TREE + CONSTRUCTOR_ROOT_NAME)
            for node_func in constructor_tmp:
                self.create_func_tree(node_func)
            self.contents.append(END_TREE + CONSTRUCTOR_ROOT_NAME)

        if func_tmp:
            self.contents.append(START_TREE + METHOD_ROOT_NAME)
            for node_func in func_tmp:
                self.create_func_tree(node_func)
            self.contents.append(END_TREE + METHOD_ROOT_NAME)

        # write class
        for node_class in class_defs:
            self.contents.append(START_TREE + CLASS_ROOT_NAME)
            self.contents.append(START_TREE + node_class.name)

            self.create_tree(node_class)

            # write base class
            if hasattr(node, "bases"):
                src = to_source(node.bases)
                self.contents.extend(get_blob(EXTEND_BLOB, src))

            self.contents.append(END_TREE + node_class.name)
            self.contents.append(END_TREE + CLASS_ROOT_NAME)

        # write others
        if others:
            self.create_other_tree(others)

    def create_func_tree(self, node):
        src = to_source(node).split('\n')

        # src[0] has def foobar(...):
        # src[4:-1] means foobar(...)
        assert src[0].startswith('def ')
        assert src[0][-1] == ':'
        function_name = src.pop(0)[4:-1]

        self.contents.append(START_TREE + function_name)
        self.contents.extend(get_blob(BODY_BLOB, src))

        args = [args.id for args in node.args.args]
        self.contents.extend(get_blob(PARAMETERS_BLOB, args))

        self.contents.append(END_TREE + function_name)

    def create_other_tree(self, node):
        src = '\n'.join(map(to_source, node)).split('\n')
        self.contents.extend(get_blob(OTHER_BLOB, src))

    def is_constructor(self, node):
        return node.name == '__new__' or node.name == '__init__'

    def write_file(self):
        self.output_file.write('\n'.join(self.contents))
        self.output_file.write('\n')
