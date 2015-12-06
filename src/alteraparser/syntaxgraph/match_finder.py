from .processor import Processor, ProcessingResult
from .vertex import VertexCategory


class MatchFinder(Processor):

    def __init__(self, input):
        self.__path = []
        self.__input = input
        self.__buffer = []
        self.__match_char = None
        self.__stopped = False
        self.__debug = False

    def process(self, vertex, path):
        if self.__stopped:
            return ProcessingResult.STOP
        if not self.__match_char:
            self.__match_char = self.__get_next_char()
        if self.__match_char:
            return self.__process_with_char_search(vertex)
        else:
            return self.__process_without_char_search(vertex)

    def undo(self, vertex, path):
        if not self.__path:
            return
        v, ch = self.__path[-1]
        if vertex is v:
            self.__path.pop()
            if ch is not None:
                if self.__match_char:
                    self.__buffer.append(self.__match_char)
                    self.__match_char = None
                self.__buffer.append(ch)
        if v.is_group_end() and v.is_rule_end:
            self.__stopped = True

    def get_path(self):
        return self.__path
    path = property(get_path)

    def get_stopped(self):
        return self.__stopped
    stopped = property(get_stopped)

    def debug_mode(self, debug=True):
        self.__debug = debug
        return self

    def __process_with_char_search(self, vertex):
        catg = vertex.get_category()
        if catg == VertexCategory.MATCHER:
            if self.__debug:
                print("Searching for '{}'".format(self.__match_char))
                print(vertex)
            if vertex.matches(self.__match_char):
                self.__path.append((vertex, self.__match_char))
                if self.__debug:
                    print('Match: {}'.format(self.__match_char))
                self.__match_char = None
                return ProcessingResult.CONTINUE
            else:
                return ProcessingResult.GO_BACK
        elif catg == VertexCategory.FINAL:
            return ProcessingResult.GO_BACK
        else:
            self.__path.append((vertex, None))
            return ProcessingResult.CONTINUE

    def __process_without_char_search(self, vertex):
        catg = vertex.get_category()
        if catg == VertexCategory.MATCHER:
            return ProcessingResult.GO_BACK
        elif catg == VertexCategory.FINAL:
            return ProcessingResult.STOP
        else:
            self.__path.append((vertex, None))
            return ProcessingResult.CONTINUE

    def __get_next_char(self):
        if self.__buffer:
            return self.__buffer.pop()
        else:
            if self.__input.has_next_char():
                return self.__input.get_next_char()
            else:
                return None