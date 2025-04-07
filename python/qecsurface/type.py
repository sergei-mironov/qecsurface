from typing import Generic, TypeVar
from dataclasses import dataclass
from enum import Enum

QuantumCircuit = TypeVar('QuantumCircuit')
QubitLabel = TypeVar('QubitLabel')


class QuantumStateLabel(Enum):
  Zero = 0
  One = 1

class QuantumOpLabel(Enum):
  X = 0
  Z = 1

@dataclass
class StabilizerTile(Generic[QubitLabel]):
  op: QuantumOpLabel
  data: list[QubitLabel]
  syndrome: QubitLabel


def mkXS(data:list[QubitLabel], syndrome:QubitLabel) -> StabilizerTile[QubitLabel]:
  return StabilizerTile[QubitLabel](QuantumOpLabel.X, data, syndrome)

def mkZS(data:list[QubitLabel], syndrome:QubitLabel) -> StabilizerTile[QubitLabel]:
  return StabilizerTile[QubitLabel](QuantumOpLabel.Z, data, syndrome)
