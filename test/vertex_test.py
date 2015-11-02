import unittest
from alteraparser.syntaxgraph.abstract_vertex import AbstractVertex
from alteraparser.syntaxgraph.processor import Processor, ProcessingResult


class TestVertex(AbstractVertex):

    def __init__(self, num):
        self.num = num

    def num_successors(self):
        return self.num - 1

    def nth_successor(self, idx):
        if 0 <= idx < self.num - 1:
            return TestVertex(idx+1)
        else:
            return None


class TestProcessor(Processor):

    def __init__(self, sum_, n):
        self.sum = sum_
        self.n = n
        self.all_summands = []

    def process(self, vertex, path):
        sum_ = sum([v.num for v, idx in path]) + vertex.num
        if ( sum_ > self.sum ) or (len(path) >= self.n):
            return ProcessingResult.GO_BACK
        elif (sum_ == self.sum) and (len(path) == self.n -1):
            summands = [v.num for v, idx in path] + [vertex.num]
            self.all_summands.append(summands)
            print(summands)


class VertexTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_walk(self):
        processor = TestProcessor(20, 3)
        for i in range(1, 10):
            vertex = TestVertex(i).walk(processor)
        self.assertEqual(len(processor.all_summands), 4)


if __name__ == "__main__":

    unittest.main()