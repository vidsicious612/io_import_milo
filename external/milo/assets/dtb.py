from dataclasses import dataclass, field
from enum import Enum

class NodeType(Enum):
    Int = 0
    Float = 1
    Variable = 2
    Func = 3
    Object = 4
    Symbol = 5
    Unhandled = 6
    IfDef = 7
    Else = 8
    EndIf = 9
    Array = 16
    Command = 17
    String = 18
    Property = 19
    Define = 32
    Include = 33
    Merge = 34
    IfNDef = 35
    Autorun = 36
    Undef = 37

@dataclass
class DTBNode:
    node_type: NodeType = NodeType.Int
    value = None
    
    def read(self, reader):
        self.node_type = NodeType(reader.int32())

        if self.node_type == NodeType.Int:
            self.value = reader.uint32()
        elif self.node_type == NodeType.Float:
            self.value = reader.float32()
        elif self.node_type in [NodeType.Variable, NodeType.Object, NodeType.Symbol, NodeType.Unhandled,
            NodeType.IfDef, NodeType.Else, NodeType.EndIf, NodeType.String,
            NodeType.Define, NodeType.Include, NodeType.Merge, NodeType.IfNDef,
            NodeType.Autorun, NodeType.Undef]:
                self.value = reader.numstring()
        elif self.node_type in [NodeType.Array, NodeType.Command, NodeType.Property]:
            dtb_parent = DTBParent()
            dtb_parent.read(reader)

            self.value = dtb_parent

    def write(self, writer):
        writer.int32(self.node_type.value)

        if self.node_type == NodeType.Int:
            writer.uint32(self.value)
        elif self.node_type == NodeType.Float:
            writer.float32(self.value)
        elif self.node_type in [NodeType.Variable, NodeType.Object, NodeType.Symbol, NodeType.Unhandled,
            NodeType.IfDef, NodeType.Else, NodeType.EndIf, NodeType.String,
            NodeType.Define, NodeType.Include, NodeType.Merge, NodeType.IfNDef,
            NodeType.Autorun, NodeType.Undef]:
                writer.numstring(self.value)
        elif self.node_type in [NodeType.Array, NodeType.Command, NodeType.Property]:
            self.value.write(writer)
        
@dataclass
class DTBParent:
    id: int = 0
    children: list[DTBNode] = field(default_factory=list)

    def read(self, reader) -> None:
        child_count = reader.ushort()

        self.id = reader.int32()

        for _ in range(child_count):
            dtb_node = DTBNode()
            dtb_node.read(reader)

            self.children.append(dtb_node)

    def write(self, writer):
        writer.ushort(len(self.children))

        writer.int32(self.id)

        for child in self.children:
            child.write(writer)

@dataclass
class DTB:
    has_tree: bool = False
    parent: DTBParent = field(default_factory=DTBParent)
    
    def read(self, reader) -> None:
        self.has_tree = reader.milo_bool()
        
        if self.has_tree == True:
            self.parent.read(reader)
    
    def write(self, writer):
        writer.milo_bool(self.has_tree)

        if self.has_tree == True:
            self.parent.write(writer)