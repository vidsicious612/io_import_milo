from . dtb import DTB

class Metadata:
    def __init__(self):
        self.revision: int = 0
        self.metadata_type: str = ""
        self.props = DTB()
        self.note: str = ""
    
    def read(self, reader):   
        self.revision = reader.int32()

        self.metadata_type = reader.numstring()
        
        self.props.read(reader)

        if self.revision > 0:
            self.note = reader.numstring()

    def write(self, writer):
        writer.int32(self.revision)

        writer.numstring(self.metadata_type)

        self.props.write(writer)

        if self.revision > 0:
            writer.numstring(self.note)