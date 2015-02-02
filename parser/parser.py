import sys
import ast
from treewriter import TreeWriter


class GitTreeCreator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.output_file = []
        self.root = []

    def parse_sourcecode(self):
        src = sys.stdin.read()
        self.write_ast_as_filetree(src)

    def write_ast_as_filetree(self, src):
        try:
            self.root = ast.parse(src)
        except:
            pass
        self.output_file = open(self.output_path, 'w')

        writer = TreeWriter(self.output_file)
        writer.write_tree(self.root)
        self.output_file.close()


def main():
    if len(sys.argv) != 2:
        print('usage : python {} <absolute path of output file>'.format(sys.argv[0]))
        return

    creator = GitTreeCreator(sys.argv[1])
    creator.parse_sourcecode()

if __name__ == '__main__':
    main()
