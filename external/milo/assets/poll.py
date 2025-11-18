class Poll:
    def __init__(self):
        self.exit: str = ""
        self.enter: str = ""

    def read(self, reader):
        self.exit = reader.numstring()
        self.enter = reader.numstring()

    def write(self, writer):
        writer.numstring(self.exit)
        writer.numstring(self.enter)