import pennylane as qml
from pennylane.tape import QuantumTape
from typing import Generic

from .type import *


QubitLabel = int
QubitValue = int
StabilizerSpec = StabilizerTile[QubitLabel]

def trace_tile(tile: StabilizerSpec) -> QubitValue:
  if tile.op == QuantumOpLabel.X:
    return trace_tile_X(tile)
  elif tile.op == QuantumOpLabel.Z:
    return trace_tile_Z(tile)
  else:
    assert False

def trace_tile_X(tile:StabilizerSpec) -> QubitValue:
  qml.Hadamard(tile.syndrome)
  for qubit_label in tile.data:
    qml.ctrl(qml.PauliX, control=tile.syndrome)(wires=[qubit_label])
  qml.Hadamard(tile.syndrome)
  return qml.measure(tile.syndrome, reset=True)

def trace_tile_Z(tile:StabilizerSpec) -> QubitValue:
  for qubit_label in tile.data:
    qml.ctrl(qml.PauliX, control=qubit_label)(wires=[tile.syndrome])
  return qml.measure(tile.syndrome, reset=True)



def test():
  s = mkXS([0, 1, 2, 3], 4)
  z = mkZS([0, 1, 2, 3], 4)

  dev = qml.device("default.qubit", wires=5)

  @qml.qnode(dev)
  def stabilizer_circuit():
    trace_tile(s)
    trace_tile(z)
    return qml.expval(qml.PauliZ(0))

  # Draw the circuit
  circuit_drawing = qml.draw(stabilizer_circuit)()
  print(circuit_drawing)

  # # Optionally, execute the circuit to see the result
  # result = stabilizer_circuit()
  # print("Circuit execution result:", result)

