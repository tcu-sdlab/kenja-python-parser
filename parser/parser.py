import sys
import ast
from treewriter import TreeWriter


class GitTreeCreator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.output_file = []
        self.source = ""
        self.root = []

    def read_file(self):
        for line in sys.stdin:
            self.source += line

    def parse_sourcecode(self):
        self.read_file()
        self.write_ast_as_filetree(self.source)

    def write_ast_as_filetree(self, source):
        try:
            self.root = ast.parse(source)
        except:
            pass
        self.output_file = open(self.output_dir, 'w')

        writer = TreeWriter(self.output_file)
        writer.write_tree(self.root)
        self.output_file.close()


def main():
    argvs = sys.argv
    if len(argvs) != 2:
        print "input error"
        print "argv : <Full path of output file>"
        return

    creator = GitTreeCreator(argvs[1])
    creator.parse_sourcecode()

if __name__ == '__main__':
    main()
