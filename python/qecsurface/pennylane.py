import pennylane as qml
from pennylane.tape import QuantumTape
from typing import Generic
from functools import partial

from .type import *
from .qeccs import *


def traverse_ftcircuit[Q](circuit: FTCircuit[Q], msms:dict) -> None:
  """ Translate FTCircuit into PennyLane operations. """

  def _traverse_op(op: FTOp[Q], msms:dict) -> None:
    if isinstance(op, FTPrim):
      for q in op.qubits:
        if op.name == OpName.X:
          qml.PauliX(wires=q)
        elif op.name == OpName.Z:
          qml.PauliZ(wires=q)
        elif op.name == OpName.H:
          qml.Hadamard(wires=q)
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
      for q in op.op.qubits:
        if op.op.name == OpName.X:
          qml.ctrl(qml.PauliX, control=op.control)(wires=q)
        elif op.op.name == OpName.Z:
          qml.ctrl(qml.PauliZ, control=op.control)(wires=q)
        else:
          raise ValueError(f"Unsupported nested op: {op.op}")
    elif isinstance(op, FTCond):
      if not isinstance(op.op, FTPrim):
        raise ValueError(f"Unsupported nested op: {op.op}")
      for q in op.op.qubits:
        if op.op.name == OpName.X:
          qml.cond(op.cond(msms),qml.PauliX)(wires=q)
        elif op.op.name == OpName.Z:
          qml.cond(op.cond(msms),qml.PauliZ)(wires=q)
        else:
          raise ValueError(f"Unsupported nested op: {op.op}")
    else:
      raise ValueError(f"Unrecognized FTOp: {op}")

  traverse_circuit(circuit, _traverse_op, msms)


def to_pennylane_mcm(c: FTCircuit[int]):
  """ Lower the FTCircuit to PennyLane. Return the PennyLane circuit returning mid-circuit
  measurement samples as a dictionary. """
  nqubits = len(labels(c))
  dev = qml.device("lightning.qubit", wires=nqubits, shots=1)
  @qml.qnode(dev, mcm_method="one-shot")
  def _circuit():
    msms = {}
    traverse_ftcircuit(c, msms)
    assert len(msms)>0, f"Expected a circuit with mid-circuit measurements"
    return {l:qml.sample(m) for l,m in msms.items()}
  return _circuit


def to_pennylane_probs(c: FTCircuit[int], data_qubits=None):
  """ Lower the FTCircuit to PennyLane. Return the PennyLane circuit returning probabilities of data
  basis vectors. """
  nqubits = len(labels(c))
  dev = qml.device("default.qubit", wires=nqubits)
  @qml.qnode(dev)
  def _circuit():
    msms = {}
    traverse_ftcircuit(c, msms)
    return qml.probs(list(range(nqubits)) if data_qubits is None else data_qubits)
  return _circuit

