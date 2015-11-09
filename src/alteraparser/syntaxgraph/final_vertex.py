from .vertex import Vertex, VertexCategory


class FinalVertex(Vertex):

    def __init__(self):
        Vertex.__init__(self, VertexCategory.FINAL)