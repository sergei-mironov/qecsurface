from typing import Generic, Union, Callable
from dataclasses import dataclass
from enum import Enum

# class QuantumStateLabel(Enum):
#   Zero = 0
#   One = 1

class OpName(Enum):
  I = 0
  X = 1
  Z = 2
  H = 3

@dataclass
class Stabilizer[Q]:
  """ A stabilizer of a CSS quantum error correction code acting on labeled qubits
  operations """
  op: OpName
  data: list[Q]

# def mkXS(data:list[QubitLabel], syndrome:QubitLabel) -> StabilizerTile[QubitLabel]:
#   return StabilizerTile[QubitLabel](QuantumOpLabel.X, data, syndrome)

# def mkZS(data:list[QubitLabel], syndrome:QubitLabel) -> StabilizerTile[QubitLabel]:
#   return StabilizerTile[QubitLabel](QuantumOpLabel.Z, data, syndrome)


##########################################

# Quantum operations
type FTOp[Q] = Union["FTPrim[Q]", "FTCond[Q]", "FTCtrl[Q]", "FTMeasure[Q]"]

@dataclass
class FTPrim[Q]:
  name:OpName
  qubit:Q

@dataclass
class FTCtrl[Q]:
  control:Q
  op:FTOp[Q]

type MeasureLabel = str

@dataclass
class FTMeasure[Q]:
  qubit:Q
  label:MeasureLabel

@dataclass
class FTCond[Q]:
  """ A quantum operation applied if a classical condition is met. """
  cond:Callable[[dict[MeasureLabel,int]],bool]
  op:FTOp[Q]

# Quantum circuits
type FTCircuit[Q] = Union["FTOps[Q]", "FTVert[Q]", "FTHor[Q]"]

@dataclass
class FTOps[Q]:
  ops:list[FTOp[Q]]

@dataclass
class FTVert[Q]:
  a: FTCircuit[Q]
  b: FTCircuit[Q]

@dataclass
class FTHor[Q]:
  a: FTCircuit[Q]
  b: FTCircuit[Q]

def labels[Q](c: FTCircuit[Q]) -> set[Q]:
  """ Collect all qubit labels of a circuit into a set."""
  acc = set()

  def _traverse_op(op: FTOp[Q]) -> None:
    if isinstance(op, (FTPrim, FTMeasure)):
      acc.add(op.qubit)
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

# \begin{itemize}
#   \item \textbf{FTPrim}: I've replaced the operation types \verb|FTX|, \verb|FTZ|, etc., with
# \verb|FTPrim|, assuming it is a new dataclass that takes \verb|OpName| as an argument to specify the
# operation type.
#   \item \textbf{OpName Matching}: The code now matches against the \verb|OpName| enumeration to
# determine the operation type.
# \end{itemize}

# Ensure \verb|FTPrim| is properly defined in your set of classes to store instances of quantum
# operations. Adjust the logic and assignments as needed to fit into your framework.


@dataclass
class QECC[Q1,Q2]:
  """ Base class for Quantum error correction codes. """
  def detect(qubit:Q1) -> tuple[FTCircuit[Q2], list[MeasureLabel]]:
    raise NotImplementedError
  def correct(qubit:Q1, ms:dict[MeasureLabel,int]) -> FTCircuit[Q2]:
    raise NotImplementedError



