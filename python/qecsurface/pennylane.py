import pennylane as qml
from pennylane.tape import QuantumTape
from typing import Generic
from functools import partial

from .type import *
from .qeccs import *


def traverse_ftcircuit(circuit: FTCircuit[int], msms):
  def _traverse_op(op: FTOp[int]):
    if isinstance(op, FTPrim):
      if op.name == OpName.X:
        qml.PauliX(wires=op.qubits)
      elif op.name == OpName.Z:
        qml.PauliZ(wires=op.qubits)
      elif op.name == OpName.H:
        qml.Hadamard(wires=op.qubits)
      elif op.name == OpName.I:
        pass
      else:
        raise ValueError(f"Unsupported primary operation: {op.name}")
    elif isinstance(op, FTInit):
      qml.StatePrep([op.alpha, op.beta], normalize=True, wires=[op.qubit])
    elif isinstance(op, FTMeasure):
      msms[op.label] = qml.measure(op.qubit, reset=True)
    elif isinstance(op, FTCtrl):
      if not isinstance(op.op, FTPrim):
        raise ValueError(f"Unsupported nested op: {op.op}")
      if op.op.name == OpName.X:
        qml.ctrl(qml.PauliX, control=op.control)(wires=op.op.qubits)
      elif op.op.name == OpName.Z:
        qml.ctrl(qml.PauliZ, control=op.control)(wires=op.op.qubits)
      else:
        raise ValueError(f"Unsupported nested op: {op.op}")
    elif isinstance(op, FTCond):
      if not isinstance(op.op, FTPrim):
        raise ValueError(f"Unsupported nested op: {op.op}")
      if op.op.name == OpName.X:
        qml.cond(op.cond(msms),qml.PauliX)(wires=op.op.qubits)
      elif op.op.name == OpName.Z:
        qml.cond(op.cond(msms),qml.PauliZ)(wires=op.op.qubits)
      else:
        raise ValueError(f"Unsupported nested op: {op.op}")
    else:
      raise ValueError(f"Unrecognized FTOp: {op}")

  def _traverse(circuit: FTCircuit[int]):
    if isinstance(circuit, FTOps):
      for op in circuit.ops:
        _traverse_op(op)
    elif isinstance(circuit, (FTHor, FTVert)):
      _traverse(circuit.a)
      _traverse(circuit.b)
    else:
      raise ValueError(f"Unrecognized FTCircuit: {circuit}")
  _traverse(circuit)


def to_pennylane_mcm(c: FTCircuit[int]):
  nqubits = len(labels(c))
  dev = qml.device("lightning.qubit", wires=nqubits, shots=3)
  @qml.qnode(dev, mcm_method="one-shot")
  def _circuit():
    msms = {}
    traverse_ftcircuit(c, msms)
    # res = [qml.sample(qml.PauliZ(w)) for w in range(nqubits)]
    res = []
    if len(msms)>0:
      res.append(qml.sample(list(msms.values())))
    # traverse_ftcircuit(c, msms)
    # if len(msms)>0:
    #   acc.append(qml.sample(list(msms.values())))
    return res
  return _circuit


def to_pennylane_probs(c: FTCircuit[int], data_qubits=None):
  nqubits = len(labels(c))
  dev = qml.device("default.qubit", wires=nqubits)
  @qml.qnode(dev)
  def _circuit():
    msms = {}
    traverse_ftcircuit(c, msms)
    return qml.probs(list(range(nqubits)) if data_qubits is None else data_qubits)
  return _circuit

