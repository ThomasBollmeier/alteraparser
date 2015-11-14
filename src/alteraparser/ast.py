class AST(object):

    def __init__(self, name, id='', text=''):
        self.__name = name
        self.id = id
        self.__children = []
        if text:
            self.__children.append(TextNode(text))

    def get_name(self):
        return self.__name
    name = property(get_name)

    def get_text(self):
        return ''.join([child.text for child in self.__children])
    text = property(get_text)

    def add_child(self, child):
        self.__children.append(child)

    def get_children(self):
        return self.__children
    children = property(get_children)

    def get_children_by_name(self, name):
        res = []
        for child in self.__children:
            if not isinstance(child, AST):
                continue
            if child.__name:
                if child.__name == name:
                    res.append(child)
            else:
                res += child.get_children_by_name(name)
        return res

    def get_children_by_id(self, id):
        res = []
        for child in self.__children:
            if not isinstance(child, AST):
                continue
            if child.__name:
                if child.id == id:
                    res.append(child)
            else:
                res += child.get_children_by_id(id)
        return res

    def __getitem__(self, key):
        if key[0] == '#':
            return self.get_children_by_id(key[1:])
        else:
            return self.get_children_by_name(key)


class TextNode(object):

    def __init__(self, text):
        self.text = text