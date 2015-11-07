class Clonable(object):

    def clone(self):
        cloned_obj = self.__class__()
        cloned_obj._on_clone_creation(self)
        return cloned_obj

    def _on_clone_creation(self, original):
        raise NotImplemented
