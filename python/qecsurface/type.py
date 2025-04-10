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

@dataclass
class Stabilizer[Q]:
  """ A CSS QECC stabilizer acting on the labeled qubits. """
  op: OpName
  data: list[Q]

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

type MeasureLabel = str

@dataclass
class FTMeasure[Q]:
  """ Quantum measure oprtation which acts on a `qubit`. Measurement result is assiciated with a
  `label`. """
  qubit:Q
  label:MeasureLabel

@dataclass
class FTCond[Q]:
  """ A quantum operation applied if a classical condition is met. """
  cond:Callable[[dict[MeasureLabel,int]],bool]
  op:FTOp[Q]

# Common type alias for quantum circuits.
type FTCircuit[Q] = Union["FTOps[Q]", "FTVert[Q]", "FTHor[Q]"]

@dataclass
class FTOps[Q]:
  """ A primitive circuit consisting of a tape of operations. """
  ops:list[FTOp[Q]]

@dataclass
class FTVert[Q]:
  """ Vertical composition of circuits, known as tensor product. """
  a: FTCircuit[Q]
  b: FTCircuit[Q]

@dataclass
class FTHor[Q]:
  """ Vertical composition of circuits, known as tensor product.
  FIXME: to be removed, since it seems equalt to FTVert. """
  a: FTCircuit[Q]
  b: FTCircuit[Q]

def labels[Q](c: FTCircuit[Q]) -> set[Q]:
  """ Collect all qubit labels from a circuit `c` into a set."""
  acc = set()

  def _traverse_op(op: FTOp[Q]) -> None:
    if isinstance(op, (FTMeasure, FTInit)):
      acc.add(op.qubit)
    elif isinstance(op, FTPrim):
      acc.update(set(op.qubits))
    elif isinstance(op, FTCtrl):
      acc.add(op.control)
      _traverse_op(op.op)
    elif isinstance(op, FTCond):
      _traverse_op(op.op)
    else:
      raise ValueError(f"Unknown operation type: {op}")

  def _traverse(circuit: FTCircuit[Q]) -> None:
    if isinstance(circuit, FTOps):
      for op in circuit.ops:
        _traverse_op(op)
    elif isinstance(circuit, (FTHor, FTVert)):
      _traverse(circuit.a)
      _traverse(circuit.b)
    else:
      raise ValueError(f"Unknown circuit type: {circuit}")

  _traverse(c)
  return acc


@dataclass
class QECC[Q1,Q2]:
  """ Base class for Quantum error correction codes. """
  def detect(qubit:Q1) -> tuple[FTCircuit[Q2], list[MeasureLabel]]:
    raise NotImplementedError
  def correct(qubit:Q1, ms:dict[MeasureLabel,int]) -> FTCircuit[Q2]:
    raise NotImplementedError



