import sys
import ast
from treewriter import TreeWriter


class GitTreeCreator:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.output_file = []
        self.source = ""
        self.root = []

    def read_file(self):
        f = open(self.input_file, 'r')
        for line in f:
            self.source += line
        f.close()

    def parse_sourcecode(self):
        self.read_file()
        self.write_ast_as_filetree(self.source)

    def write_ast_as_filetree(self, source):
        self.root = ast.parse(source)
        self.output_file = open(self.output_dir + '/out', 'w')

        writer = TreeWriter(self.output_file)
        writer.write_tree(self.root)
        self.output_file.close()

def main():
    argvs = sys.argv
    if len(argvs) != 3:
        print "input error"
        print "argv : <Path of input file> <Path of output directory>"
        return

    creator = GitTreeCreator(argvs[1], argvs[2])
    creator.parse_sourcecode()

if __name__ == '__main__':
    main()

