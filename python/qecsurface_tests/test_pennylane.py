import pytest
from numpy.testing import assert_allclose
from qecsurface import *
from qecsurface.qeccs import (
  surface20u_detect, surface20u_print, surface17u_detect, surface17u_print
)

def test_to_pennylane_mcm():
  circuit_ft = FTHor(
    FTOps([
      FTPrim(OpName.I, [0]),  # Initialize qubit 0 if needed (placeholder)
      FTCtrl(0, FTPrim(OpName.X, [1])),
      FTMeasure(0, "m0"),
      FTMeasure(1, "m1")
    ]),
    FTVert(
      FTOps([
        FTCond(lambda m: 2*m["m0"]+m["m1"] == 2, FTPrim(OpName.X, [2]))  # Conditional X on qubit 2
      ]),
      FTOps([
        FTCond(lambda m: m["m1"] == 1, FTPrim(OpName.X, [2]))  # Conditional Z on qubit 2
      ])
    )
  )
  cPL = to_pennylane_mcm(circuit_ft)
  print(qml.draw(cPL)())


def test_tile_X_to_pennylane_mcm():
  s = Stabilizer(OpName.X, [0, 1, 2, 3])
  c = stabilizer_tile_X(s, 4, "m")
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


def test_tile_Z_to_pennylane_mcm():
  s = Stabilizer(OpName.Z, [0, 1, 2, 3])
  c = stabilizer_tile_Z(s, 4, "m")
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


def test_surface9():
  c = surface9([0,1,2,3,4], [5,6,7,8])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


def test_surface9_run():
  c = surface9([0,1,2,3,4], [5,6,7,8])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())
  print(cPL())

def test_surface20u_detect1():
  c,l = surface20u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())
  print(l)
  msms = cPL()
  print(msms)
  # print(len(res[0]))
  print(surface20u_print(msms,l))

def test_surface17u_print():
  msms = {(0,'T',l):1 for l in range(8)}
  print(surface17u_print(msms, list(msms.keys())))

def test_surface17u_detect2():
  init = FTOps([FTPrim(OpName.H,[0,1,2,3,4,5,6,7,8])])
  c1,l1 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  cPL = to_pennylane_mcm(reduce(FTHor,[init,c1,c2]))
  print(qml.draw(cPL)())
  # print(l2)
  msms = cPL()
  # print(res)
  # print(len(res[0]))
  print(surface17u_print(msms, l1))
  print(surface17u_print(msms, l2))


def test_surface17u_detect3():
  init = FTOps([FTPrim(OpName.H,[0,1,2,3,4,5,6,7,8])])
  c1,l1 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  err =  FTOps([FTPrim(OpName.Z,[4])])
  c3,l3 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 2)
  cPL = to_pennylane_mcm(reduce(FTHor,[init,c1,c2,err,c3]))
  # print(qml.draw(cPL)())
  # print(l2)
  msms = cPL()
  # print(res)
  # print(len(res[0]))
  print(surface17u_print(msms, l1))
  print(surface17u_print(msms, l2))
  print(surface17u_print(msms, l3))


def test_surface20u_detect2():
  c1,l1 = surface20u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface20u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  cPL = to_pennylane_mcm(reduce(FTHor,[c1,c2]))
  print(qml.draw(cPL)())
  # print(l2)
  msms = cPL()
  # print(res)
  # print(len(res[0]))
  print(surface20u_print(msms, l1))
  print(surface20u_print(msms, l2))


def test_surface20u_print():
  msms = {(0,'T',l):1 for l in range(12)}
  print(surface20u_print(msms, list(msms.keys())))

def test_surface25():
  c = surface25([*range(13)], [*range(13,25)])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


# def test_surface25_run():
#   c = surface25([*range(13)], [*range(13,25)])
#   cPL = to_pennylane_mcm(c)
#   print(qml.draw(cPL)())
#   print(cPL())


def test_bitflip_detect():
  c = bitflip_detect([*range(0,3)], [*range(3,5)])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())
  # print(cPL())


def test_bitflip_init():
  i = FTOps([FTInit(0, 1/2, 1/2)])
  c = bitflip_encode(0, [0,1,2])
  cPL = to_pennylane_probs(FTVert(i,c), [0,1,2])
  print(qml.draw(cPL)())
  print(cPL())


def test_bitflip_encode():
  c = bitflip_encode(0, [0,1,2])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


def test_bitflip_encode_detect():
  e = bitflip_encode(0, [0,1,2])
  c = bitflip_detect([0,1,2],[3,4])
  cPL = to_pennylane_mcm(FTVert(e,c))
  print(qml.draw(cPL)())


def test_bitflip_correct():
  d = bitflip_detect([0,1,2],[3,4])
  c = bitflip_correct([0,1,2])
  cPL = to_pennylane_mcm(FTVert(d,c))
  print(qml.draw(cPL)())


DATA_QUBITS = [0, 1, 2]
@pytest.mark.parametrize("e", DATA_QUBITS)
def test_bitflip_full(e):
  data = DATA_QUBITS
  syndrome = [3, 4]
  cPL = to_pennylane_probs(reduce(FTHor, [
    FTOps([FTInit(0, 1/2, 1/2)]),
    bitflip_encode(0, data),
    FTOps([FTPrim(OpName.X, [e])]),
    bitflip_detect(data, syndrome),
    bitflip_correct(data),
  ]), data)
  print(qml.draw(cPL)())
  probs = cPL()
  assert_allclose(probs, [0.5, 0.,  0.,  0.,  0.,  0.,  0.,  0.5])

