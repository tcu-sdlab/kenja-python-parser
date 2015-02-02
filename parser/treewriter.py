import ast
import cStringIO
from unparse import Unparser


CLASS_ROOT_NAME = '[CN]'
TREE = '[TN]'
START_TREE = '[TS]'
END_TREE = '[TE]'
METHOD_ROOT_NAME = '[MT]'
BLOB = '[BN]'
BLOB_INFO = '[BI]'
BODY_BLOB = 'body'
PARAMETERS_BLOB = 'parameters'

CONSTRUCTOR_ROOT_NAME = '[CS]'
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

        if hasattr(node, "body"):
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
                self.contents.append(START_TREE + ' ' + CONSTRUCTOR_ROOT_NAME + '\n')
                for node_func in constructor_tmp:
                    self.create_func_tree(node_func)
                self.contents.append(END_TREE + ' ' + CONSTRUCTOR_ROOT_NAME + '\n')

            if len(func_tmp) != 0:
                self.contents.append(START_TREE + ' ' + METHOD_ROOT_NAME + '\n')
                for node_func in func_tmp:
                    self.create_func_tree(node_func)
                self.contents.append(END_TREE + ' ' + METHOD_ROOT_NAME + '\n')

            # write class
            for node_class in class_def:
                self.contents.append(START_TREE + ' ' + CLASS_ROOT_NAME + '\n')
                self.contents.append(START_TREE + ' ' + node_class.name + '\n')

                self.create_tree(node_class)

                # write base class
                if hasattr(node, "bases"):
                    out = cStringIO.StringIO()
                    Unparser(node.bases, out)
                    src = out.getvalue()
                    self.contents.append(BLOB + ' ' + EXTEND_BLOB + '\n')
                    self.contents.append(BLOB_INFO + ' ' + '1' + '\n')
                    self.contents.append(src + '\n')

                self.contents.append(END_TREE + ' ' + node_class.name + '\n')
                self.contents.append(END_TREE + ' ' + CLASS_ROOT_NAME + '\n')

            # write other
            if len(other) != 0:
                self.create_other_tree(other)
        else:
            pass

    def create_func_tree(self, node):
        out = cStringIO.StringIO()
        Unparser(node, out)
        src = out.getvalue().split('\n')

        self.contents.append(START_TREE + ' ' + src[2][4:-1] + '\n')
        self.contents.append(BLOB + ' ' + BODY_BLOB + '\n')
        self.contents.append(BLOB_INFO + ' ' + str(len(src[3:])) + '\n')

        for line in src[3:]:
            self.contents.append(line + '\n')

        self.contents.append(BLOB + ' ' + PARAMETERS_BLOB + '\n')
        self.contents.append(BLOB_INFO + ' ' + str(len(node.args.args)) + '\n')

        for args in node.args.args:
            self.contents.append(args.id + '\n')

        self.contents.append(END_TREE + ' ' + src[2][4:-1] + '\n')

    def create_other_tree(self, node):
        out = cStringIO.StringIO()
        Unparser(node, out)
        src = out.getvalue().split('\n')

        self.contents.append(BLOB + ' ' + OTHER_BLOB + '\n')
        self.contents.append(BLOB_INFO + ' ' + str(len(src) - 1) + '\n')

        for line in src[1:]:
            self.contents.append(line + '\n')

    def is_constructor(self, node):
        out = cStringIO.StringIO()
        Unparser(node, out)
        src = out.getvalue().split('\n')

        if (src[2][4:11] == "__new__") or (src[2][4:12] == "__init__"):
            return True
        else:
            return False

    def write_file(self):
        for line in self.contents:
            self.output_file.write(line)
