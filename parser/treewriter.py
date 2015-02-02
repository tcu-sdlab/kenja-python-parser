import ast
import cStringIO
from astor import to_source
from unparse import Unparser


TREE = '[TN] '
START_TREE = '[TS] '
END_TREE = '[TE] '
BLOB = '[BN] '
BLOB_INFO = '[BI] '

CLASS_ROOT_NAME = '[CN]'
CONSTRUCTOR_ROOT_NAME = '[CS]'
METHOD_ROOT_NAME = '[MT]'
BODY_BLOB = 'body'
PARAMETERS_BLOB = 'parameters'
EXTEND_BLOB = 'extend'
OTHER_BLOB = 'other'


class TreeWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.contents = []

    def write_tree(self, node):
        self.create_tree(node)
        self.write_file()

    def create_tree(self, node):
        class_def = []
        func_def = []
        other = []

        if not hasattr(node, 'body'):
            return

        for child in node.body:
            if isinstance(child, ast.ClassDef):
                class_def.append(child)
            elif isinstance(child, ast.FunctionDef):
                func_def.append(child)
            else:
                other.append(child)

        # write func
        constructor_tmp = []
        func_tmp = []
        for node_func in func_def:
            if self.is_constructor(node_func):
                constructor_tmp.append(node_func)
            else:
                func_tmp.append(node_func)

        if len(constructor_tmp) != 0:
            self.contents.append(START_TREE + CONSTRUCTOR_ROOT_NAME)
            for node_func in constructor_tmp:
                self.create_func_tree(node_func)
            self.contents.append(END_TREE + CONSTRUCTOR_ROOT_NAME)

        if len(func_tmp) != 0:
            self.contents.append(START_TREE + METHOD_ROOT_NAME)
            for node_func in func_tmp:
                self.create_func_tree(node_func)
            self.contents.append(END_TREE + METHOD_ROOT_NAME)

        # write class
        for node_class in class_def:
            self.contents.append(START_TREE + CLASS_ROOT_NAME)
            self.contents.append(START_TREE + node_class.name)

            self.create_tree(node_class)

            # write base class
            if hasattr(node, "bases"):
                out = cStringIO.StringIO()
                Unparser(node.bases, out)
                src = out.getvalue()
                self.contents.append(BLOB + EXTEND_BLOB)
                self.contents.append(BLOB_INFO + '1')
                self.contents.append(src)

            self.contents.append(END_TREE + node_class.name)
            self.contents.append(END_TREE + CLASS_ROOT_NAME)

        # write other
        if len(other) != 0:
            self.create_other_tree(other)

    def create_func_tree(self, node):
        out = cStringIO.StringIO()
        Unparser(node, out)
        src = out.getvalue().split('\n')

        self.contents.append(START_TREE + src[2][4:-1])
        self.contents.append(BLOB + BODY_BLOB)
        self.contents.append(BLOB_INFO + str(len(src[3:])))

        for line in src[3:]:
            self.contents.append(line)

        self.contents.append(BLOB + PARAMETERS_BLOB)
        self.contents.append(BLOB_INFO + str(len(node.args.args)))

        for args in node.args.args:
            self.contents.append(args.id)

        self.contents.append(END_TREE + src[2][4:-1])

    def create_other_tree(self, node):
        self.contents.append(BLOB + OTHER_BLOB)

        src = '\n'.join(map(to_source, node)).split('\n')
        self.contents.append('{0}{1}'.format(BLOB_INFO, len(src)))

        self.contents.extend(src)

    def is_constructor(self, node):
        out = cStringIO.StringIO()
        Unparser(node, out)
        src = out.getvalue().split('\n')

        if (src[2][4:11] == "__new__") or (src[2][4:12] == "__init__"):
            return True
        else:
            return False

    def write_file(self):
        self.output_file.write('\n'.join(self.contents))
        self.output_file.write('\n')
