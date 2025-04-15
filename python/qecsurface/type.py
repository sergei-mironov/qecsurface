""" A minimalistic domain-specific language for experimenting with fault-tolerant quantum computing.
The DSL is designed with the idea of enabling nested error correction codes. Most of the types
accept `Q` which is a type of qubit label, typically `int`.
"""
from typing import Generic, Union, Callable
from dataclasses import dataclass
from enum import Enum

class OpName(Enum):
  """ Quantum operation labels """
  I = 0
  X = 1
  Z = 2
  H = 3

def opname2str(n:OpName)->str:
  return {OpName.I:'I', OpName.H:'H', OpName.Z:'Z', OpName.X:'X'}[n]

# Common type alias for quantum operations
type FTOp[Q] = Union["FTInit[Q]", "FTPrim[Q]", "FTCond[Q]", "FTCtrl[Q]", "FTMeasure[Q]"]

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

# Syndrome test measurement label encodes a layer, the syndrome type and the qubit labels
type MeasureLabel[Q] = tuple[int,OpName,tuple[Q,...]]

@dataclass
class FTMeasure[Q]:
  """ Quantum measure oprtation which acts on a `qubit`. Measurement result is assiciated with a
  `label`. """
  qubit:Q
  label:MeasureLabel[Q]

@dataclass
class FTCond[Q]:
  """ A quantum operation applied if a classical condition is met. """
  cond:Callable[[dict[MeasureLabel[Q],int]],bool]
  op:FTOp[Q]

# Common type alias for quantum circuits, where Q is type of qubit label.
type FTCircuit[Q] = Union["FTOps[Q]", "FTComp[Q]"]

@dataclass
class FTOps[Q]:
  """ A primitive circuit consisting of a tape of operations. """
  ops:list[FTOp[Q]]

@dataclass
class FTComp[Q]:
  """ Vertical composition of circuits, also known as circuit tensor product. """
  a: FTCircuit[Q]
  b: FTCircuit[Q]



def traverse_circuit[Q](
  circuit: FTCircuit[Q],
  op_handler: Callable[[FTOp[Q], Union[dict, set]], None],
  acc: Union[dict, set]
) -> None:
  """ Generalized function for traversing FTCircuit and performing an operation using a handler.
  """
  def _traverse_op(op: FTOp[Q]) -> None:
    op_handler(op, acc)

  def _traverse(circuit: FTCircuit[Q]) -> None:
    if isinstance(circuit, FTOps):
      for op in circuit.ops:
        _traverse_op(op)
    elif isinstance(circuit, FTComp):
      _traverse(circuit.a)
      _traverse(circuit.b)
    else:
      raise ValueError(f"Unrecognized FTCircuit: {circuit}")

  _traverse(circuit)


def labels[Q](c: FTCircuit[Q]) -> set[Q]:
  """ Collect all qubit labels from a circuit `c` into a set. """

  def _traverse_op(op: FTOp[Q], acc: set[Q]) -> None:
    # Handler for different operation types
    if isinstance(op, (FTMeasure, FTInit)):
      acc.add(op.qubit)
    elif isinstance(op, FTPrim):
      acc.update(set(op.qubits))
    elif isinstance(op, FTCtrl):
      acc.add(op.control)
      _traverse_op(op.op, acc)
    elif isinstance(op, FTCond):
      _traverse_op(op.op, acc)
    else:
      raise ValueError(f"Unrecognized FTOp: {op}")

  acc = set()
  traverse_circuit(c, _traverse_op, acc)
  return acc


@dataclass
class QECC[Q1,Q2]:
  """ Base class for Quantum error correction codes. """
  def detect(qubit:Q1) -> tuple[FTCircuit[Q2], list[MeasureLabel[Q2]]]:
    raise NotImplementedError
  def correct(qubit:Q1, ms:dict[MeasureLabel,int]) -> FTCircuit[Q2]:
    raise NotImplementedError

