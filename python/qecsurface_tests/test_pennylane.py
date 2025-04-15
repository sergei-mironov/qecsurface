import pytest
from numpy.testing import assert_allclose
from qecsurface import *
from qecsurface.qeccs import (
  surface20u_detect, surface20u_print, surface17u_detect, surface17u_print,
  surface25u_detect, surface25u_print2, surface25u_print, surface25u_correct
)

def test_to_pennylane_mcm():
  circuit_ft = FTComp(
    FTOps([
      FTPrim(OpName.I, [0]),
      FTCtrl(0, FTPrim(OpName.X, [1])),
      FTMeasure(0, "m0"),
      FTMeasure(1, "m1")
    ]),
    FTComp(
      FTOps([
        FTCond(lambda m: 2*m["m0"]+m["m1"] == 2, FTPrim(OpName.X, [2]))
      ]),
      FTOps([
        FTCond(lambda m: m["m1"] == 1, FTPrim(OpName.X, [2]))
      ])
    )
  )
  cPL = to_pennylane_mcm(circuit_ft)
  print(qml.draw(cPL)())


def test_tile_X_to_pennylane_mcm():
  s = FTPrim(OpName.X, [0, 1, 2, 3])
  c = stabilizer_test_X(s, 4, "m")
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())


def test_tile_Z_to_pennylane_mcm():
  s = FTPrim(OpName.Z, [0, 1, 2, 3])
  c = stabilizer_test_Z(s, 4, "m")
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
  print(surface20u_print(msms,l))

def test_surface17u_print():
  msms = {(0,OpName.X,l):1 for l in range(8)}
  print(surface17u_print(msms, list(msms.keys())))

def test_surface17u_detect2():
  init = FTOps([FTPrim(OpName.H,[0,1,2,3,4,5,6,7,8])])
  c1,l1 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  cPL = to_pennylane_mcm(reduce(FTComp,[init,c1,c2]))
  print(qml.draw(cPL)())
  msms = cPL()
  print(surface17u_print(msms, l1))
  print(surface17u_print(msms, l2))


def test_surface17u_detect3():
  init = FTOps([FTPrim(OpName.H,[0,1,2,3,4,5,6,7,8])])
  c1,l1 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  err =  FTOps([FTPrim(OpName.Z,[4])])
  c3,l3 = surface17u_detect([0,1,2,3,4,5,6,7,8], [9], 2)
  cPL = to_pennylane_mcm(reduce(FTComp,[init,c1,c2,err,c3]))
  msms = cPL()
  print(surface17u_print(msms, l1))
  print(surface17u_print(msms, l2))
  print(surface17u_print(msms, l3))


def test_surface20u_detect2():
  c1,l1 = surface20u_detect([0,1,2,3,4,5,6,7,8], [9], 0)
  c2,l2 = surface20u_detect([0,1,2,3,4,5,6,7,8], [9], 1)
  cPL = to_pennylane_mcm(reduce(FTComp,[c1,c2]))
  print(qml.draw(cPL)())
  msms = cPL()
  print(surface20u_print(msms, l1))
  print(surface20u_print(msms, l2))


def test_surface25u_detect2():
  data = list(range(13))
  syndrome = [13]
  c1,l1 = surface25u_detect(data, syndrome, 0)
  c2,l2 = surface25u_detect(data, syndrome, 1)
  cPL = to_pennylane_mcm(reduce(FTComp,[c1,c2]))
  print(qml.draw(cPL)())
  msms = cPL()
  print(surface25u_print(msms, l1))
  print(surface25u_print(msms, l2))


SURFACE25U_DATA_QUBITS = list(range(13))
@pytest.mark.parametrize("error_qubit", SURFACE25U_DATA_QUBITS)
@pytest.mark.parametrize("error_op", [OpName.H, OpName.X, OpName.Z])
def test_surface25u_correct(error_qubit, error_op):
  """ Surface25 Quantum Error Correction Code[1] (with unified syndrome qubits) error correction
  cycle. The error correction routine corrects any single data qubit Pauli error.

  The simplifications are as follows: (1) Syndrome qubits are considered to be perfect; (2)
  Therefore, Hadamard check circuits are applied to data qubits without a specific order; (3)
  Further, to enhance simulation speed, all syndrome qubits are represented using a single qubit
  which is re-used after each syndrome measurement.

  [1] - https://arxiv.org/pdf/1404.3747
  """
  # Technical details:
  #
  # The desired quantum circuit is first defined in a minimalistic EDSL from the `qecsurface.type`
  # module. Various subcuruit building routines are defined in `qecsurface.qeccs`.  The result is
  # then lowered to PennyLane and simulated.
  #
  # (a) - Initialize the logical-zero state; (b) - Introduce a data qubit error; (c) - Define an
  # error detection circuit; (d) - Apply corrections using a trivial decoding protocol; (e) - Define
  # the error detection for the second time; (f) - Stack the resulting circuits and convert them to
  # the PennyLane format and (g) - Obtain the mid-circuitmeasurement samples (msms) by running the
  # simulation.
  data = SURFACE25U_DATA_QUBITS
  syndrome = [13]
  layer0,layer1,layer2 = 0,1,2
  c1,l1 = surface25u_detect(data, syndrome, layer0)          # (a)
  err = FTOps([FTPrim(error_op,[error_qubit])])              # (b)
  c2,l2 = surface25u_detect(data, syndrome, layer1)          # (c)
  corr = surface25u_correct(data, layer0, layer1)            # (d)
  c3,l3 = surface25u_detect(data, syndrome, layer2)          # (e)
  cPL = to_pennylane_mcm(reduce(FTComp,[c1,err,c2,corr,c3])) # (f)
  msms = cPL()                                               # (g)
  expected = surface25u_print2(msms, l1)
  assert all(e not in expected for e in "XZ"), f"Errors in the zero state:\n{expected}"
  synd = surface25u_print2(msms, l2)
  print("Error syndrome:")
  print(synd)
  assert any(e in synd for e in "XZ"), f"Errors not found in the syndrome:\n{synd}"
  actual = surface25u_print2(msms, l3)
  assert actual == expected, f"Correction failed:\n{actual}"


def test_surface20u_print():
  msms = {(0,OpName.X,l):1 for l in range(12)}
  print(surface20u_print(msms, list(msms.keys())))

def test_surface25():
  c = surface25([*range(13)], [*range(13,25)])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())

def test_bitflip_detect():
  c = bitflip_detect([*range(0,3)], [*range(3,5)])
  cPL = to_pennylane_mcm(c)
  print(qml.draw(cPL)())
  # print(cPL())


def test_bitflip_init():
  i = FTOps([FTInit(0, 1/2, 1/2)])
  c = bitflip_encode(0, [0,1,2])
  cPL = to_pennylane_probs(FTComp(i,c), [0,1,2])
  print(qml.draw(cPL)())
  print(cPL())


def test_bitflip_encode():
  c = bitflip_encode(0, [0,1,2])
  cPL = to_pennylane_probs(c)
  print(qml.draw(cPL)())


def test_bitflip_encode_detect():
  e = bitflip_encode(0, [0,1,2])
  c = bitflip_detect([0,1,2],[3,4])
  cPL = to_pennylane_mcm(FTComp(e,c))
  print(qml.draw(cPL)())


def test_bitflip_correct():
  d = bitflip_detect([0,1,2],[3,4])
  c = bitflip_correct([0,1,2])
  cPL = to_pennylane_mcm(FTComp(d,c))
  print(qml.draw(cPL)())


BITFLIP_DATA_QUBITS = [0, 1, 2]
@pytest.mark.parametrize("e", BITFLIP_DATA_QUBITS)
def test_bitflip_full(e):
  data = BITFLIP_DATA_QUBITS
  syndrome = [3, 4]
  cPL = to_pennylane_probs(reduce(FTComp, [
    FTOps([FTInit(0, 1/2, 1/2)]),
    bitflip_encode(0, data),
    FTOps([FTPrim(OpName.X, [e])]),
    bitflip_detect(data, syndrome),
    bitflip_correct(data),
  ]), data)
  print(qml.draw(cPL)())
  probs = cPL()
  assert_allclose(probs, [0.5, 0.,  0.,  0.,  0.,  0.,  0.,  0.5])


def test_map_bitflip():
  c1 = FTOps([
    FTInit(qubit=0, alpha=1.0, beta=0.0),
    FTPrim(name=OpName.X, qubits=[0])
  ])
  c2 = map_circuit(c1, Bitflip(qmap={0: ([0,1,2], [3,4])}))
  cPL = to_pennylane_probs(c2)
  print(qml.draw(cPL)())

