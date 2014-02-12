import ast
import StringIO
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

        for child in node.body:
            if isinstance(child, ast.ClassDef):
                class_def.append(child)

            elif isinstance(child, ast.FunctionDef):
                func_def.append(child)

        #write func
        self.contents.append(START_TREE + ' ' + METHOD_ROOT_NAME + '\n')
        for node_func in func_def:
            self.create_func_tree(node_func)
        self.contents.append(END_TREE + ' ' + METHOD_ROOT_NAME + '\n')

        #write class
        self.contents.append(START_TREE + ' ' + CLASS_ROOT_NAME + '\n')
        for node_class in class_def:
            out = StringIO.StringIO()
            Unparser(node_class, out)
            src = out.getvalue().split('\n')

            self.contents.append(START_TREE + ' ' + node_class.name + '\n')
            self.create_tree(node_class)
            self.contents.append(END_TREE + ' ' + node_class.name + '\n')
        self.contents.append(END_TREE + ' ' + CLASS_ROOT_NAME + '\n')

    def create_func_tree(self, node):
        out = StringIO.StringIO()
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

    def write_file(self):
        for line in self.contents:
            self.output_file.write(line)
