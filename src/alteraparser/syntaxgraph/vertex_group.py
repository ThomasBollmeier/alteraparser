from .dockable import Dockable
from .clonable import Clonable
from .vertex import Vertex, VertexCategory


class StartVertex(Vertex):

    def __init__(self, vertex_group):
        Vertex.__init__(self, VertexCategory.GROUP_START)
        self.__group = vertex_group
        self.name = None
        self.id = None

    def num_successors(self):
        if not self.__group._VertexGroup__expanded:
            self.__group.expand()
        return Vertex.num_successors(self)

    def nth_successor(self, idx):
        if not self.__group._VertexGroup__expanded:
            self.__group.expand()
        return Vertex.nth_successor(self, idx)


class EndVertex(Vertex):

    def __init__(self):
        Vertex.__init__(self, VertexCategory.GROUP_END)
        self.name = None
        self.id = None
        self.ignore = False
        self.transform_ast_fn = lambda ast: ast
        self.is_rule_end = False


class VertexGroup(Dockable, Clonable):

    def __init__(self):
        self.__expanded = False
        self.__start = StartVertex(self)
        self.__end = EndVertex()

    def set_name(self, name):
        res = self.clone()
        res.__start.name = name
        res.__end.name = name
        return res

    def get_name(self):
        return self.__start.name

    name = property(get_name, set_name)

    def set_id(self, id):
        res = self.clone()
        res.__start.id = id
        res.__end.id = id
        return res

    def get_id(self):
        return self.__start.id

    id = property(get_id, set_id)

    def set_ignore(self, ignore=True):
        self.__end.ignore = ignore
        return self

    def transform_ast(self, transformer_fn):
        res = self.clone()
        res._VertexGroup__end.transform_ast_fn = transformer_fn
        return res

    def set_unique(self, is_unique=True):
        res = self.clone()
        res._VertexGroup__end.is_rule_end = is_unique
        return res

    def connect(self, dockable):
        self.__end.connect(dockable)
        return dockable

    def get_dock_vertex(self):
        return self.__start

    def expand(self):
        if not self.__expanded:
            start = Vertex()
            end = Vertex()
            self.__start.connect(start)
            end.connect(self.__end)
            self._on_expand(start, end)
            self.__expanded = True

    def _on_expand(self, start, end):
        pass

    def _on_clone_creation(self, original):
        self.__start.name = self.__end.name = original.__start.name
        self.__start.id = self.__end.id = original.__start.id
        self.__end.ignore = original.__end.ignore
        self.__end.transform_ast_fn = original.__end.transform_ast_fn
        self.__end.is_rule_end = original.__end.is_rule_end


class Multiples(VertexGroup):

    def __init__(self, element=None, min_occur=0, max_occur=None):
        VertexGroup.__init__(self)
        if element:
            self.__element = element.clone()
        else:
            self.__element = None
        self.__min_occur = min_occur
        self.__max_occur = max_occur

    def _on_expand(self, start, end):
        current = start
        for _ in range(self.__min_occur):
            current = current.connect(self.__element.clone())
        min_end = current
        if self.__max_occur is None:
            if current is not start:
                current.connect(current)
            else:
                elem = self.__element.clone()
                start.connect(elem).connect(start)
                elem.connect(end)
        else:
            delta = self.__max_occur - self.__min_occur
            for _ in range(delta):
                current = current.connect(self.__element.clone())
                current.connect(end)
        min_end.connect(end)

    def _on_clone_creation(self, original):
        VertexGroup._on_clone_creation(self, original)
        self.__element = original.__element.clone()
        self.__min_occur = original.__min_occur
        self.__max_occur = original.__max_occur


class Branches(VertexGroup):

    def __init__(self):
        VertexGroup.__init__(self)
        self.__branches = []

    def add_branch(self, elements):
        self.__branches.append([el.clone() for el in elements])

    def _on_expand(self, start, end):
        for branch in self.__branches:
            curr = start
            for elem in branch:
                curr = curr.connect(elem)
            curr.connect(end)

    def _on_clone_creation(self, original):
        VertexGroup._on_clone_creation(self, original)
        self.__branches = [[el.clone() for el in orig_branch] for orig_branch in original.__branches]
