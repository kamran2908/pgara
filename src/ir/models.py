from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, Any

@dataclass(frozen=True)
class Value:
    name: str

@dataclass
class Instruction:
    opcode: str
    result: Optional[Value] = None
    operands: List[Value] = field(default_factory=list)
    raw_text: str = ""
    source_line: int = -1
    # For phi nodes: list of (incoming_value, predecessor_label)
    # incoming_value can be Value or a constant.
    incoming_values: List[Tuple[Any, str]] = field(default_factory=list)
    # For terminators: list of target labels
    target_labels: List[str] = field(default_factory=list)
    
    @property
    def is_phi(self) -> bool:
        return self.opcode == "phi"
        
    @property
    def is_terminator(self) -> bool:
        # Standard LLVM terminators that affect CFG
        return self.opcode in ("br", "ret", "switch", "invoke", "resume", "unreachable", "indirectbr", "cleanupret", "catchret", "catchswitch")
        
    def defs(self) -> Set[Value]:
        return {self.result} if self.result else set()
        
    def uses(self) -> Set[Value]:
        # Uses include operands and incoming_values if they are instances of Value
        use_set = set(self.operands)
        for val, _ in self.incoming_values:
            if isinstance(val, Value):
                use_set.add(val)
        return use_set

@dataclass(eq=False)
class BasicBlock:
    label: str
    instructions: List[Instruction] = field(default_factory=list)
    predecessors: Set['BasicBlock'] = field(default_factory=set)
    successors: Set['BasicBlock'] = field(default_factory=set)
    loop_depth: int = 0
    live_in: Set[Value] = field(default_factory=set)
    live_out: Set[Value] = field(default_factory=set)
    
    @property
    def terminator(self) -> Optional[Instruction]:
        if self.instructions and self.instructions[-1].is_terminator:
            return self.instructions[-1]
        return None
        
    @property
    def phis(self) -> List[Instruction]:
        return [inst for inst in self.instructions if inst.is_phi]
        
    @property
    def non_phi_instructions(self) -> List[Instruction]:
        return [inst for inst in self.instructions if not inst.is_phi]

@dataclass
class Function:
    name: str
    arguments: List[Value] = field(default_factory=list)
    blocks: List[BasicBlock] = field(default_factory=list)
    entry_block: Optional[BasicBlock] = None

@dataclass
class Module:
    functions: List[Function] = field(default_factory=list)
