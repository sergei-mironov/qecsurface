from qecsurface import *

def test_to_pennylane_mcm():
  circuit_ft = FTHor(
    FTOps([
      FTPrim(OpName.I, 0),  # Initialize qubit 0 if needed (placeholder)
      FTCtrl(0, FTPrim(OpName.X, 1)),
      FTMeasure(0, "m0"),
      FTMeasure(1, "m1")
    ]),
    FTVert(
      FTOps([
        FTCond(lambda m: 2*m["m0"]+m["m1"] == 2, FTPrim(OpName.X, 2))  # Conditional X on qubit 2
      ]),
      FTOps([
        FTCond(lambda m: m["m1"] == 1, FTPrim(OpName.X, 2))  # Conditional Z on qubit 2
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


def test_bitflip_full():
  data = [0,1,2]
  syndrome = [3,4]
  i = FTOps([FTInit(0, 1/2, 1/2)])
  e = bitflip_encode(0, data)
  err = FTOps([FTPrim(OpName.X, 2)])
  d = bitflip_detect(data, syndrome)
  c = bitflip_correct(data)
  cPL = to_pennylane_probs(reduce(FTHor,[i,e,err,d,c]), data)
  print(qml.draw(cPL)())
  print(cPL())
