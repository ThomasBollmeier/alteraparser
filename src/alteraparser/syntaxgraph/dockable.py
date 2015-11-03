class Dockable(object):

    def connect(self, dockable):
        raise NotImplemented

    def get_dock_vertex(self):
        """
        Return vertex that can be docked
        """
        raise NotImplemented
