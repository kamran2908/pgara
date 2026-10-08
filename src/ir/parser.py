import re
from src.ir.models import Value, Instruction, BasicBlock, Function, Module

class ParseError(Exception):
    pass

SUPPORTED_OPCODES = {
    "br", "add", "phi", "icmp", "sext", "ret", "getelementptr", 
    "load", "mul", "sub", "call", "sdiv", "store", "switch", 
    "and", "or", "xor", "unreachable"
}

def is_type(t):
    return t.startswith('%struct.') or t.startswith('%class.') or t.startswith('%union.') or t.startswith('%enum.')

def extract_local_values(text):
    tokens = re.findall(r'%[A-Za-z0-9_.]+', text)
    return [Value(t) for t in tokens if not is_type(t)]

def parse_instruction(line, line_num, filepath):
    line_clean = line.split(';', 1)[0].strip()
    if not line_clean:
        return None
    
    # Check for result assignment
    lhs_match = re.match(r'^(\s*%[A-Za-z0-9_.]+)\s*=\s*(.*)', line_clean)
    if lhs_match:
        result_val = Value(lhs_match.group(1).strip())
        rhs = lhs_match.group(2).strip()
    else:
        result_val = None
        rhs = line_clean

    # Opcode
    opcode_match = re.match(r'^([a-z]+)\b(.*)', rhs)
    if not opcode_match:
        raise ParseError(f"Cannot parse opcode at {filepath}:{line_num}\n{line}")
    opcode = opcode_match.group(1)
    if opcode not in SUPPORTED_OPCODES:
        raise ParseError(f"Unsupported opcode '{opcode}' at {filepath}:{line_num}\n{line}")
        
    rest = opcode_match.group(2)
    inst = Instruction(opcode=opcode, result=result_val, raw_text=line.strip(), source_line=line_num)
    
    if opcode == "phi":
        pairs = re.findall(r'\[\s*([^,]+?)\s*,\s*([^\]]+?)\s*\]', rest)
        for val_str, pred_str in pairs:
            if val_str.startswith('%') and not is_type(val_str):
                val = Value(val_str)
            else:
                val = val_str
            inst.incoming_values.append((val, pred_str.strip()))
            
    elif opcode in ("br", "switch"):
        targets = re.findall(r'label\s+(%[A-Za-z0-9_.]+)', rest)
        inst.target_labels = targets
        rest_no_labels = re.sub(r'label\s+%[A-Za-z0-9_.]+', '', rest)
        inst.operands = extract_local_values(rest_no_labels)
        
    elif opcode == "ret":
        inst.operands = extract_local_values(rest)
        
    elif opcode == "unreachable":
        pass
        
    else:
        # call, add, icmp, load, store, etc.
        rest_no_labels = re.sub(r'label\s+%[A-Za-z0-9_.]+', '', rest)
        inst.operands = extract_local_values(rest_no_labels)
        
    return inst

def parse_module(filepath):
    module = Module()
    current_func = None
    current_bb = None

    with open(filepath, 'r', encoding='utf-8') as f:
        accumulated_line = ""
        accumulated_line_num = 0
        bracket_count = 0
        
        for line_num, line in enumerate(f, 1):
            line_clean = line.split(';', 1)[0].strip()
            if not line_clean and not accumulated_line:
                continue
                
            if accumulated_line:
                accumulated_line += " " + line_clean
            else:
                accumulated_line = line_clean
                accumulated_line_num = line_num
                
            bracket_count += line_clean.count('[') - line_clean.count(']')
            if bracket_count > 0:
                continue
                
            line_to_process = accumulated_line
            accumulated_line = ""
            bracket_count = 0
            
            if not line_to_process:
                continue
                
            if line_to_process.startswith('define '):
                func_name_match = re.search(r'@([A-Za-z0-9_.]+)', line_to_process)
                func_name = func_name_match.group(1) if func_name_match else "unknown"
                
                arg_start = line_to_process.find('(')
                arg_end = line_to_process.find(')')
                if arg_start != -1 and arg_end != -1:
                    arg_str = line_to_process[arg_start+1:arg_end]
                    args = extract_local_values(arg_str)
                else:
                    args = []
                    
                current_func = Function(name=func_name, arguments=args)
                current_bb = None
                continue
                
            if line_to_process == '}':
                if current_func:
                    if current_bb:
                        current_func.blocks.append(current_bb)
                    module.functions.append(current_func)
                    current_func = None
                continue
                
            if current_func is None:
                continue
                
            # Block label check
            label_match = re.match(r'^([A-Za-z0-9_.]+):$', line_to_process)
            if label_match:
                if current_bb:
                    current_func.blocks.append(current_bb)
                current_bb = BasicBlock(label=label_match.group(1))
                if current_func.entry_block is None:
                    current_func.entry_block = current_bb
                continue
                
            # Instruction processing
            if current_bb is None:
                current_bb = BasicBlock(label="<implicit_entry>")
                current_func.entry_block = current_bb
                
            inst = parse_instruction(line_to_process, accumulated_line_num, filepath)
            if inst:
                current_bb.instructions.append(inst)
                
    return module
