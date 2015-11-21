import os


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

    def get_own_text(self):
        return ''.join([tn.text for tn in self.__children
                        if isinstance(tn, TextNode)])
    own_text = property(get_own_text)

    def add_child(self, child, pos=None):
        if pos is None:
            self.__children.append(child)
        else:
            self.__children.insert(pos, child)

    def get_children(self):
        return self.__children
    children = property(get_children)

    def get_ast_children(self):
        return [ast for ast in self.__children if isinstance(ast, AST)]
    ast_children = property(get_ast_children)

    def get_children_by_name(self, name, recursive=True):
        res = []
        for child in self.__children:
            if not isinstance(child, AST):
                continue
            if child.__name == name:
                res.append(child)
            elif recursive and not child.__name:
                res += child.get_children_by_name(name)
        return res

    def get_children_by_id(self, id_, recursive=True):
        res = []
        for child in self.__children:
            if not isinstance(child, AST):
                continue
            if child.id == id_:
                res.append(child)
            elif recursive and not child.__name:
                res += child.get_children_by_id(id_)
        return res

    def __getitem__(self, key):
        if key[0] == '#':
            return self.get_children_by_id(key[1:])
        else:
            return self.get_children_by_name(key)

    def to_xml(self, indent_size=2):
        intro = '<?xml version="1.0"?>'
        return intro + os.linesep + self._to_xml('', 0, indent_size)

    def _to_xml(self, xml, indent, indent_size):
        name = self.__name or 'ast'
        new_xml = ' ' * (indent*indent_size)
        new_xml += '<{}'.format(name)
        if self.id:
            new_xml += ' id = "{}"'.format(self.id)
        text = self.own_text
        children = self.ast_children
        closed = False
        if text or children:
            new_xml += '>'
        else:
            new_xml += '/>'
            closed = True
        if text:
            new_xml += text
        if children:
            for child in children:
                new_xml = child._to_xml(new_xml, indent+1, indent_size)
        if not closed:
            if children:
                new_xml += os.linesep + ' ' * (indent*indent_size)
            new_xml += '</{}>'.format(name)
        if xml:
            return xml + os.linesep + new_xml
        else:
            return new_xml


class TextNode(object):

    def __init__(self, text):
        self.text = text
