import pennylane as qml
from pennylane.tape import QuantumTape
from typing import Generic
from functools import partial

from .type import *
from .qeccs import *

# QubitLabel = int
# QubitValue = int
# StabilizerSpec = StabilizerTile[QubitLabel]

# def trace_tile(tile: StabilizerSpec) -> QubitValue:
#   if tile.op == QuantumOpLabel.X:
#     return trace_tile_X(tile)
#   elif tile.op == QuantumOpLabel.Z:
#     return trace_tile_Z(tile)
#   else:
#     assert False

# def trace_tile_X(tile:StabilizerSpec) -> QubitValue:
#   qml.Hadamard(tile.syndrome)
#   for qubit_label in tile.data:
#     qml.ctrl(qml.PauliX, control=tile.syndrome)(wires=[qubit_label])
#   qml.Hadamard(tile.syndrome)
#   return qml.measure(tile.syndrome, reset=True)

# def trace_tile_Z(tile:StabilizerSpec) -> QubitValue:
#   for qubit_label in tile.data:
#     qml.ctrl(qml.PauliX, control=qubit_label)(wires=[tile.syndrome])
#   return qml.measure(tile.syndrome, reset=True)



def to_pennylane(c: FTCircuit[int]) -> None:
  nqubits = len(labels(c))
  dev = qml.device("default.qubit", wires=nqubits, shots=3)
  msmts = {}

  @qml.qnode(dev, mcm_method="one-shot")
  def _circuit():
    def _traverse(circuit: FTCircuit[int]):
      def _traverse_op(op: FTOp[int]):
        if isinstance(op, FTPrim):
          if op.name == OpName.X:
            qml.PauliX(wires=op.qubit)
          elif op.name == OpName.Z:
            qml.PauliZ(wires=op.qubit)
          elif op.name == OpName.H:
            qml.Hadamard(wires=op.qubit)
          elif op.name == OpName.I:
            pass
          else:
            raise ValueError(f"Unsupported primary operation: {op.name}")
        elif isinstance(op, FTMeasure):
          msmts[op.label] = qml.measure(op.qubit, reset=True)
        elif isinstance(op, FTCtrl):
          if not isinstance(op.op, FTPrim):
            raise ValueError(f"Unsupported nested op: {op.op}")
          if op.op.name == OpName.X:
            qml.ctrl(qml.PauliX, control=op.control)(wires=op.op.qubit)
          elif op.op.name == OpName.Z:
            qml.ctrl(qml.PauliZ, control=op.control)(wires=op.op.qubit)
          else:
            raise ValueError(f"Unsupported nested op: {op.op}")
        elif isinstance(op, FTCond):
          if not isinstance(op.op, FTPrim):
            raise ValueError(f"Unsupported nested op: {op.op}")
          if op.op.name == OpName.X:
            qml.cond(op.cond(msmts),qml.PauliX)(wires=op.op.qubit)
          elif op.op.name == OpName.Z:
            qml.cond(op.cond(msmts),qml.PauliZ)(wires=op.op.qubit)
          else:
            raise ValueError(f"Unsupported nested op: {op.op}")
        else:
          raise ValueError(f"Unrecognized FTOp: {op}")

      if isinstance(circuit, FTOps):
        for op in circuit.ops:
          _traverse_op(op)
      elif isinstance(circuit, (FTHor, FTVert)):
        _traverse(circuit.a)
        _traverse(circuit.b)
      else:
        raise ValueError(f"Unrecognized FTCircuit: {circuit}")

    _traverse(c)
    return qml.sample(tuple(msmts.values()))
  return _circuit


def test_to_pennylane():
  circuit_ft = FTHor(
    FTOps([
      FTPrim(OpName.I, 0),  # Initialize qubit 0 if needed (placeholder)
      FTCtrl(0, FTPrim(OpName.X, 1)),
      FTMeasure(0, "m0"),
      FTMeasure(1, "m1")
    ]),
    FTVert(
      FTOps([
        FTCond(lambda m: m["m0"] == 1, FTPrim(OpName.X, 2))  # Conditional X on qubit 2
      ]),
      FTOps([
        FTCond(lambda m: m["m1"] == 1, FTPrim(OpName.X, 2))  # Conditional Z on qubit 2
      ])
    )
  )
  cPL = to_pennylane(circuit_ft)
  print(qml.draw(cPL)())


def test_tile_X_to_pennylane():
  s = Stabilizer(OpName.X, [0, 1, 2, 3])
  c = stabilizer_tile_X(s, 4, "m")
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())

def test_tile_Z_to_pennylane():
  s = Stabilizer(OpName.Z, [0, 1, 2, 3])
  c = stabilizer_tile_Z(s, 4, "m")
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())


def test_surface9():
  c = surface9([0,1,2,3,4], [5,6,7,8])
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())


def test_surface9_run():
  c = surface9([0,1,2,3,4], [5,6,7,8])
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())
  print(cPL())

def test_surface25():
  c = surface25([*range(13)], [*range(13,25)])
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())


def test_surface25_run():
  c = surface25([*range(13)], [*range(13,25)])
  cPL = to_pennylane(c)
  print(qml.draw(cPL)())
  print(cPL())

# def test():
#   s = mkXS([0, 1, 2, 3], 4)
#   z = mkZS([0, 1, 2, 3], 4)

#   dev = qml.device("default.qubit", wires=5)

#   @qml.qnode(dev)
#   def stabilizer_circuit():
#     trace_tile(s)
#     trace_tile(z)
#     return qml.expval(qml.PauliZ(0))

#   # Draw the circuit
#   circuit_drawing = qml.draw(stabilizer_circuit)()
#   print(circuit_drawing)

  # # Optionally, execute the circuit to see the result
  # result = stabilizer_circuit()
  # print("Circuit execution result:", result)

