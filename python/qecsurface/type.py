""" A minimalistic domain-specific language for experimenting with fault-tolerant quantum computing.
The DSL is designed with the idea of enabling nested error correction codes. Most of the types
accept `Q` which is a type of qubit label, typically `int`.
"""
from typing import Generic, Union, Callable
from dataclasses import dataclass
from enum import Enum

# Quantum operation definitions {{{

class OpName(Enum):
  """ Quantum operation labels """
  I = 0
  X = 1
  Z = 2
  H = 3

def opname2str(n:OpName)->str:
  return {OpName.I:'I', OpName.H:'H', OpName.Z:'Z', OpName.X:'X'}[n]

# Common type alias for quantum operations
type FTOp[Q] = Union["FTInit[Q]", "FTPrim[Q]", "FTCond[Q]", "FTCtrl[Q]", "FTMeasure[Q]",
                     "FTErr[Q]"]

@dataclass
class FTInit[Q]:
  """ Primitive quantum operation acting on one qubit. """
  qubit:Q
  alpha:complex
  beta:complex

@dataclass
class FTPrim[Q]:
  """ Primitive quantum operation acting on one qubit. """
  name:OpName
  qubits:list[Q]

@dataclass
class FTCtrl[Q]:
  """ Quantum control operation acting on two qubits. """
  control:Q
  op:FTOp[Q]

# Syndrome test measurement label encodes the layer number, the syndrome type (typically, X/Z) and
# the date qubit labels involved in the measuremenr.
# FIXME: Is it tuple[Q,...] or just Q?
type MeasureLabel[Q] = tuple[int,OpName,tuple[Q,...]]

@dataclass
class FTMeasure[Q]:
  """ Quantum measure oprtation which acts on a `qubit`. Measurement result is assiciated with a
  `label`. """
  qubit:Q
  label:MeasureLabel[Q]


type FTExpr[Q] = Union["FTExprRef[Q]", "FTExprFun[Q]"]

@dataclass
class FTExprFun[Q]:
    func: Union["xor", "and", "or", "eq"]
    args: list[FTExpr[Q]]

@dataclass
class FTExprRef[Q]:
    m: MeasureLabel[Q]

@dataclass
class FTCond[Q]:
  """ A quantum operation applied if a classical condition is met. """
  cond:Callable[[dict[MeasureLabel[Q],int]],bool]
  op:FTOp[Q]

@dataclass
class FTErr[Q]:
  """ Apply an error to `phys` physical qubit constituting the logical qubit Q. """
  qubit:Q
  phys:int
  name:OpName

# }}}

# Quantum circuit definitions {{{

# Common type alias for quantum circuits, where Q is type of qubit label.
type FTCircuit[Q] = Union["FTOps[Q]", "FTComp[Q]"]

@dataclass
class FTOps[Q]:
  """ A primitive circuit consisting of a tape of operations. """
  ops:list[FTOp[Q]]

@dataclass
class FTComp[Q]:
  """ Composition of circuits, also known as circuit tensor product. """
  a: FTCircuit[Q]
  b: FTCircuit[Q]

# }}}

def traverse_circuit[Q,A](
  circuit:FTCircuit[Q],
  op_handler:Callable[[FTOp[Q],A],A],
  acc:A
) -> None:
  """ Generalized function for traversing FTCircuit and performing an operation using a handler.
  """
  def _traverse_op(op:FTOp[Q], acc:A) -> A:
    return op_handler(op, acc)

  def _traverse(circuit:FTCircuit[Q], acc) -> A:
    if isinstance(circuit, FTOps):
      for op in circuit.ops:
        acc = _traverse_op(op, acc)
    elif isinstance(circuit, FTComp):
      acc = _traverse(circuit.a, acc)
      acc = _traverse(circuit.b, acc)
    else:
      raise ValueError(f"Unrecognized FTCircuit: {circuit}")
    return acc

  return _traverse(circuit, acc)


def labels[Q](c:FTCircuit[Q]) -> set[Q]:
  """ Collect all qubit labels from a circuit `c` into a set. """

  def _traverse_op(op:FTOp[Q], acc:set[Q]) -> None:
    # Handler for different operation types
    if isinstance(op, (FTMeasure, FTInit)):
      acc.add(op.qubit)
    elif isinstance(op, FTPrim):
      acc.update(set(op.qubits))
    elif isinstance(op, FTCtrl):
      acc.add(op.control)
      acc = _traverse_op(op.op, acc)
    elif isinstance(op, FTCond):
      acc = _traverse_op(op.op, acc)
    elif isinstance(op, FTErr):
      acc.add(op.qubit)
    else:
      raise ValueError(f"Unrecognized FTOp: {op}")
    return acc

  acc = set()
  traverse_circuit(c, _traverse_op, acc)
  return acc


# Circuit mapping {{{

@dataclass
class Map[Q1,Q2]:
  """ Base class for stateful circuit mapping algorithms. """
  def map_op(self, op:FTOp[Q1]) -> FTCircuit[Q2]:
    """ Maps an operation of a source circuit into a destination circuit. """
    raise NotImplementedError


def map_circuit[Q1,Q2](c:FTCircuit[Q1], m:Map[Q1,Q2]) -> FTCircuit[Q2]:
  """ Maps the circuit `c` by mapping each its operation and taking a compostion """
  def _traverse_op(op:FTOp[Q1], acc) -> None:
    return FTComp(acc, m.map_op(op))
  return traverse_circuit(c, _traverse_op, FTOps([]))

# }}}


