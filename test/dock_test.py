import unittest
from alteraparser.syntaxgraph.vertex import Vertex
from alteraparser.syntaxgraph.vertex_group import VertexGroup
from alteraparser.syntaxgraph.processor import Processor


class TestGroup(VertexGroup):

    def __init__(self, size):
        VertexGroup.__init__(self)
        self.__size = size

    def _on_expand(self, start, end):
        for _ in range(self.__size):
            start.connect(Vertex()).connect(end)


class TestProcessor(Processor):

    def __init__(self):
        self.count = 0
        self.visited = set()

    def process(self, vertex, path):
        if vertex not in self.visited:
            self.count += 1
            self.visited.add(vertex)

    def undo(self, vertex, path):
        pass


class DockTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_docking(self):
        processor = TestProcessor()
        size = 5

        begin = Vertex()
        begin.connect(TestGroup(size)).connect(Vertex())
        begin.walk(processor)

        self.assertEqual(processor.count, 4 + size)


if __name__ == '__main__':

    unittest.main()