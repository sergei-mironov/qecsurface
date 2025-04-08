from functools import reduce
from .type import *


def stabilizer_tile_X[Q](tile:Stabilizer[Q], syndrome:Q, ml:MeasureLabel) -> FTCircuit[Q]:
  assert tile.op == OpName.X, tile
  return FTOps([
    FTPrim(OpName.H, syndrome),
    *[FTCtrl(control=syndrome, op=FTPrim(OpName.X, qubit_label))
      for qubit_label in tile.data
    ],
    FTPrim(qubit=syndrome, name=OpName.H),
    FTMeasure(qubit=syndrome, label=ml)
  ])

def stabilizer_tile_Z[Q](tile: Stabilizer[Q], syndrome: Q, ml: MeasureLabel) -> FTCircuit[Q]:
  assert tile.op == OpName.Z, tile
  return FTOps([
    *[FTCtrl(control=qubit_label, op=FTPrim(OpName.X, syndrome))
      for qubit_label in tile.data
    ],
    FTMeasure(qubit=syndrome, label=ml)
  ])

def stabX(data, syndrome):
  return stabilizer_tile_X(Stabilizer(OpName.X, data), syndrome, str(syndrome))
def stabZ(data, syndrome):
  return stabilizer_tile_Z(Stabilizer(OpName.Z, data), syndrome, str(syndrome))


def surface9[Q](data:list[Q], syndrome:list[Q]) -> FTCircuit[Q]:
  """ Top-left corner of surface25 code, not really supposed to work. """
  assert len(data)==5
  assert len(syndrome)==4
  d0,d1,d3,d5,d6 = [*data]
  s13,s15,s16,s18 = [*syndrome]
  tiles = [
    stabilizer_tile_X(Stabilizer(OpName.X, [d0,d1,d3]), s13, "s13"),
    stabilizer_tile_Z(Stabilizer(OpName.Z, [d0,d3,d5]), s15, "s15"),
    stabilizer_tile_Z(Stabilizer(OpName.Z, [d1,d3,d6]), s16, "s16"),
    stabilizer_tile_X(Stabilizer(OpName.X, [d3,d5,d6]), s18, "s18"),
  ]
  return reduce(FTVert, tiles)


def surface25[Q](data: list[Q], syndrome: list[Q]) -> FTCircuit[Q]:
  """ Top-left corner of surface25 code, not really supposed to work. """
  assert len(data) == 13
  assert len(syndrome) == 12
  d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12 = [*data]
  s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24 = [*syndrome]

  tiles = [
              stabX([d0,d1,d3],s13), stabX([d1,d2,d4],s14),
    stabZ([d0,d3,d5],s15), stabZ([d1,d3,d4,d6],s16), stabZ([d2,d4,d7],s17),
           stabX([d3,d5,d6,d8],s18), stabX([d4,d6,d7,d9],s19),
    stabZ([d5,d8,d10],s20), stabZ([d6,d8,d9,d11],s21), stabZ([d7,d9,d12],s22),
              stabX([d8,d10,d11],s23), stabX([d9,d11,d12],s24),
  ]
  return reduce(FTVert, tiles)

@dataclass
class SurfaceQECC[Q1,Q2](QECC[Q1,Q2]):
  def detect(qubit:Q1) -> tuple[FTCircuit[Q2], list[MeasureLabel]]:
    raise NotImplementedError
  def correct(qubit:Q1, ms:dict[MeasureLabel,int]) -> FTCircuit[Q2]:
    raise NotImplementedError




