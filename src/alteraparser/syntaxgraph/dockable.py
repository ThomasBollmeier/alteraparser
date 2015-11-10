class Dockable(object):

    def connect(self, dockable):
        raise NotImplemented

    def __gt__(self, other):
        self.connect(other)
        return other

    def get_dock_vertex(self):
        """
        Return vertex that can be docked
        """
        raise NotImplemented
