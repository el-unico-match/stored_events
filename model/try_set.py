class try_set:
    def __init__(self, source, source_key):
        self.source = source
        self.source_key = source_key

    def to(self, target, target_key):
        if self.source is not None and self.source[self.source_key] is not None:
            target[target_key] = self.source[self.source_key]