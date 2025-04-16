""" The module defines QECC circuit parts. """
from functools import reduce
from textwrap import dedent
from dataclasses import field
from collections import defaultdict
from .type import *


def stabilizer_test_X[Q](tile:FTPrim[Q], syndrome:Q, ml:MeasureLabel[Q]) -> FTCircuit[Q]:
  """ Define a stabilizer X-test circuit. """
  assert tile.name == OpName.X, tile
  return FTOps([
    FTPrim(OpName.H, [syndrome]),
    *[FTCtrl(control=syndrome, op=FTPrim(OpName.X, [qubit_label]))
      for qubit_label in tile.qubits
    ],
    FTPrim(OpName.H, [syndrome]),
    FTMeasure(qubit=syndrome, label=ml)
  ])

def stabilizer_test_Z[Q](tile:FTPrim[Q], syndrome:Q, ml:MeasureLabel[Q]) -> FTCircuit[Q]:
  """ Define a stabilizer Z-test circuit. """
  assert tile.name == OpName.Z, tile
  return FTOps([
    *[FTCtrl(control=qubit_label, op=FTPrim(OpName.X, [syndrome]))
      for qubit_label in tile.qubits
    ],
    FTMeasure(qubit=syndrome, label=ml)
  ])


def surface9[Q](data:list[Q], syndrome:list[Q], layer:int=0) -> FTCircuit[Q]:
  """ Top-left corner of surface25 code, not really supposed to work. """
  assert len(data)==5
  assert len(syndrome)==4

  def SX(data, syndrome):
    return stabilizer_test_X(FTPrim(OpName.X, data), syndrome, (layer,OpName.X,tuple(data)))
  def SZ(data, syndrome):
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, (layer,OpName.Z,tuple(data)))

  d0,d1,d3,d5,d6 = [*data]
  s13,s15,s16,s18 = [*syndrome]
  tiles = [
    SX([d0,d1,d3], s13),
    SZ([d0,d3,d5], s15),
    SZ([d1,d3,d6], s16),
    SX([d3,d5,d6], s18),
  ]
  return reduce(FTComp, tiles)


def surface25[Q](data: list[Q], syndrome: list[Q]) -> FTCircuit[Q]:
  assert len(data) == 13
  assert len(syndrome) == 12
  d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12 = [*data]
  s13, s14, s15, s16, s17, s18, s19, s20, s21, s22, s23, s24 = [*syndrome]

  def SX(data, syndrome):
    return stabilizer_test_X(FTPrim(OpName.X, data), syndrome, str(syndrome))
  def SZ(data, syndrome):
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, str(syndrome))

  tiles = [
              SX([d0,d1,d3],s13), SX([d1,d2,d4],s14),
    SZ([d0,d3,d5],s15), SZ([d1,d3,d4,d6],s16), SZ([d2,d4,d7],s17),
           SX([d3,d5,d6,d8],s18), SX([d4,d6,d7,d9],s19),
    SZ([d5,d8,d10],s20), SZ([d6,d8,d9,d11],s21), SZ([d7,d9,d12],s22),
              SX([d8,d10,d11],s23), SX([d9,d11,d12],s24),
  ]
  return reduce(FTComp, tiles)


def surface25u_detect[Q](# {{{
  data: list[Q], syndrome: list[Q], layer:int=0
) -> tuple[FTCircuit[Q],list[MeasureLabel]]:
  """ Build the surface25u error detection circuit. Return the circuit alongside with a list of
  mid-circuit measurement labels. """
  assert len(data) == 13, f"Expected 13 data qubit labels, got {data}"
  assert len(syndrome) == 1, f"Expected 1 syndrome qubit label, got {syndrome}"

  d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12 = [*data]
  s, = [*syndrome]
  labels = []

  def SX(data, syndrome):
    label = (layer,OpName.X,tuple(data))
    labels.append(label)
    return stabilizer_test_X(FTPrim(OpName.X, data), syndrome, label)
  def SZ(data, syndrome):
    label = (layer,OpName.Z,tuple(data))
    labels.append(label)
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, label)

  tiles = [
              SX([d0,d1,d3],s), SX([d1,d2,d4],s),
    SZ([d0,d3,d5],s), SZ([d1,d3,d4,d6],s), SZ([d2,d4,d7],s),
           SX([d3,d5,d6,d8],s), SX([d4,d6,d7,d9],s),
    SZ([d5,d8,d10],s), SZ([d6,d8,d9,d11],s), SZ([d7,d9,d12],s),
              SX([d8,d10,d11],s), SX([d9,d11,d12],s),
  ]
  return reduce(FTComp, tiles), labels
# }}}


def surface25u_print(msms:dict[MeasureLabel,int], flt:list[MeasureLabel]):
  """ Visualize the surface25 syndromes. """
  return dedent('''
    o ? o ? o
    ? o ? o ?
    o ? o ? o
    ? o ? o ?
    o ? o ? o
  ''').replace('?','%s') % tuple((opname2str(l[1]) if msms[l] == 1 else ' ') for l in flt)


def surface25u_print2(msms:dict[MeasureLabel,int], flt:list[MeasureLabel], ref_layer:int=0):# {{{
  """ Visualize the surface25 syndromes. Highlight only those syndromes that mismatch the layer-0
  syndromes. """
  return dedent('''
    o ? o ? o
    ? o ? o ?
    o ? o ? o
    ? o ? o ?
    o ? o ? o
  ''').replace('?','%s') % tuple(
    (opname2str(l[1]) if msms[l] != msms[(ref_layer,*l[1:])] else ' ') for l in flt
  )
# }}}

def surface25u_correct[Q](data:list[Q], layer0:int, layer:int) -> FTCircuit[Q]:# {{{
  """ Build the surface25u error correction circuit assuming `layer` measurememnts are available.
  Use `layer0` measurements as a reference. """
  def _corrector(op, opc, d):
    def _cond(msms):
      neigb = [l[2] for l in list(msms.keys()) if l[0]==layer and l[1]==op and (d in l[2])]
      others = [l[2] for l in list(msms.keys()) if l[0]==layer and l[1]==op and (d not in l[2])]
      return reduce(
        lambda a,b: a & b, [
          *[(msms[(layer0,op,n)] != msms[(layer,op,n)]) for n in neigb],
          *[(msms[(layer0,op,n)] == msms[(layer,op,n)]) for n in others],
        ]
      )
    return FTCond(_cond, FTPrim(opc,[d]))
  return FTComp(
    FTOps([_corrector(OpName.X, OpName.Z, d) for d in data]),
    FTOps([_corrector(OpName.Z, OpName.X, d) for d in data])
  )
# }}}

def surface17u_detect[Q](
  data: list[Q], syndrome: list[Q], layer:int=0
) -> tuple[FTCircuit[Q], list[MeasureLabel]]:
  assert len(data) == 9
  assert len(syndrome) == 1
  d0, d1, d2, d3, d4, d5, d6, d7, d8  = [*data]
  s, = [*syndrome]
  labels = []

  def SX(data, syndrome):
    label = (layer,OpName.X,tuple(data))
    labels.append(label)
    return stabilizer_test_X(FTPrim(OpName.X, data), syndrome, label)
  def SZ(data, syndrome):
    label = (layer,OpName.Z,tuple(data))
    labels.append(label)
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, label)

  tiles = [
    #SX([d0,d8],s),
    #SZ([d0,d1],s),
    SX([d1,d2],s),
    #SZ([d2,d6],s),

    SZ([d0,d3],s),
    SX([d0,d1,d3,d4],s), SZ([d1,d2,d4,d5],s),
    #SX([d2,d5],s),
    #SX([d3,d6],s),
    SZ([d3,d4,d6,d7],s), SX([d4,d5,d8,d7],s),
    SZ([d5,d8],s),
    SX([d6,d7],s),
    #SZ([d7,d8],s),
  ]
  return reduce(FTComp, tiles), labels


def surface17u_print(msms:dict[MeasureLabel,int], flt:list[MeasureLabel]):
  return dedent('''
            %s
     o    o    o
  %s    %s    %s
     o    o    o
       %s    %s    %s
     o    o    o
       %s
  ''') % tuple((opname2str(l[1]) if msms[l] == 1 else ' ') for l in flt)


def surface20u_detect[Q](
  data: list[Q], syndrome: list[Q], layer:int=0
) -> tuple[FTCircuit[Q], list[MeasureLabel]]:
  assert len(data) == 9
  assert len(syndrome) == 1
  d0, d1, d2, d3, d4, d5, d6, d7, d8  = [*data]
  s, = [*syndrome]
  labels = []

  def SX(data, syndrome):
    label = (layer,OpName.X,tuple(data))
    labels.append(label)
    return stabilizer_test_X(FTPrim(OpName.X, data), syndrome, label)
  def SZ(data, syndrome):
    label = (layer,OpName.Z,tuple(data))
    labels.append(label)
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, label)

  tiles = [
    #SX([d0,d8],s),
    SZ([d0,d1],s),
    SX([d1,d2],s),
    #SZ([d2,d6],s),

    SZ([d0,d3],s),
    SX([d0,d1,d3,d4],s), SZ([d1,d2,d4,d5],s),
    SX([d2,d5],s),
    SX([d3,d6],s),
    SZ([d3,d4,d6,d7],s), SX([d4,d5,d8,d7],s),
    SZ([d5,d8],s),
    SX([d6,d7],s),
    SZ([d7,d8],s),
  ]
  return reduce(FTComp, tiles), labels


def surface20u_print(msms:dict[MeasureLabel,int], flt:list[MeasureLabel]):
  return dedent('''
       %s    %s
     o    o    o
  %s    %s    %s    %s
     o    o    o
  %s    %s    %s    %s
     o    o    o
        %s   %s
  ''') % tuple((opname2str(l[1]) if msms[l] == 1 else ' ') for l in flt)


# def surface17B_correct[Q](data: list[Q], syndrome: list[Q], labels:set[str]) -> FTCircuit[Q]:
#   return reduce(FTComp, tiles)


def bitflip_encode[Q](src:Q, out:list[Q]) -> FTCircuit[Q]:
  assert src in out, "source qubit must be among the output ones"
  d0, d1 = [q for q in out if q != src]
  return FTOps([ FTCtrl(src, FTPrim(OpName.X, [d0])), FTCtrl(src, FTPrim(OpName.X, [d1])) ])


def bitflip_detect[Q](data:list[Q], syndrome:list[Q], layer:int=0) -> FTCircuit[Q]:
  d0, d1, d2 = [*data]
  s1, s2 = [*syndrome]
  def SZ(data, syndrome):
    return stabilizer_test_Z(FTPrim(OpName.Z, data), syndrome, (layer,OpName.Z,tuple(data)))
  tiles = [ SZ([d0, d1], s1), SZ([d1, d2], s2) ]
  return reduce(FTComp, tiles)


def bitflip_correct[Q](data:list[Q], layer:int=0) -> FTCircuit[Q]:
  d0, d1, d2 = [*data]
  ee = lambda msms, d: msms[(layer, OpName.Z, d)]
  e0 = lambda msms:    ee(msms,(d0,d1))  & (~ee(msms,(d1,d2)))
  e1 = lambda msms:    ee(msms,(d0,d1))  &   ee(msms,(d1,d2))
  e2 = lambda msms:  (~ee(msms,(d0,d1))) &   ee(msms,(d1,d2))
  return FTOps([FTCond(e0, FTPrim(OpName.X, [d0])),
                FTCond(e1, FTPrim(OpName.X, [d1])),
                FTCond(e2, FTPrim(OpName.X, [d2]))])

# Bitflip {{{
@dataclass
class Bitflip[Q1,Q2](Map[Q1,Q2]):
  """ Maps quantum circuit into a quantum circuit with Bitflip quantum error correction. """
  qmap:dict[Q1,tuple[list[Q2],list[Q2]]]
  layer:int = 0

  def _next_layer(self) -> int:
    l = self.layer
    self.layer = self.layer + 1
    return l

  def _error_correction_cycle(self, q:Q1) -> FTCircuit[Q2]:
    qubits, syndromes = self.qmap[q]
    layer = self._next_layer()
    det = bitflip_detect(qubits, syndromes, layer)
    corr = bitflip_correct(qubits, layer)
    return FTComp(det,corr)

  def map_op(self, op:FTOp[Q1]) -> FTCircuit[Q2]:
    qmap = self.qmap
    acc = []
    if isinstance(op, FTInit):
      q = op.qubit
      acc.append(FTOps([FTInit(qmap[q][0][0], op.alpha, op.beta)]))
      acc.append(bitflip_encode(qmap[q][0][0], qmap[q][0]))
    elif isinstance(op, FTErr):
      q = op.qubit
      qubits = qmap[q][0]
      equbit = qubits[op.phys % len(qubits)]
      acc.append(FTOps([FTPrim(op.name, [equbit])]))
      acc.append(self._error_correction_cycle(q))
    elif isinstance(op, FTPrim):
      for q in op.qubits:
        qubits = qmap[q][0]
        if op.name == OpName.I:
          pass
        elif op.name == OpName.X:
          acc.append(FTOps([FTPrim(OpName.X, qubits)]))
        elif op.name == OpName.Z:
          acc.append(FTOps([FTPrim(OpName.Z, qubits)]))
        else:
          raise ValueError(f"Bitflip qecc: Unsupported primitive operation: {op}")
        acc.append(self._error_correction_cycle(q))
    else:
      raise ValueError(f"Bitflip qecc: Unsupported operation: {op}")
    return reduce(FTComp, acc)
# }}}

# Surface25u {{{
@dataclass
class Surface25u[Q1, Q2](Map[Q1, Q2]):
  qmap: dict[Q1, tuple[list[Q2], Q2]]
  _layer: int = 0
  _layers0: dict[Q1, int] = field(default_factory=dict)
  _mls: dict[Q1, list[MeasureLabel]] = field(default_factory=lambda: defaultdict(list))

  def _next_layer(self) -> int:
    l = self._layer
    self._layer += 1
    return l

  def _error_correction_cycle(self, q:Q1, layer0:int) -> FTCircuit[Q2]:
    qubits, syndrome = self.qmap[q]
    layer = self._next_layer()
    det, ml = surface25u_detect(qubits, [syndrome], layer)
    corr = surface25u_correct(qubits, layer0, layer)
    self._mls[q].append(ml)
    return FTComp(det,corr)

  def map_op(self, op: FTOp[Q1]) -> FTCircuit[Q2]:
    qmap = self.qmap
    layers0 = self._layers0
    acc = []
    if isinstance(op, FTInit):
      if (op.alpha, op.beta) != (1.0, 0.0):
        raise ValueError(f"Surface25u could only be initialized with |0> (got {op})")
      q = op.qubit
      qubits, syndrome = qmap[q]
      layers0[q] = self._next_layer()
      c, ml = surface25u_detect(qubits, [syndrome], layers0[q])
      self._mls[q].append(ml)
      acc.append(c)
    elif isinstance(op, FTErr):
      q = op.qubit
      if layers0.get(q) is None:
        raise ValueError(f"Surface25u: qubit {q} was not initialized")
      qubits,_ = qmap[q]
      equbit = qubits[op.phys % len(qubits)]
      acc.append(FTOps([FTPrim(op.name, [equbit])]))
      acc.append(self._error_correction_cycle(q, layers0[q]))
    elif isinstance(op, FTPrim):
      for q in op.qubits:
        if layers0.get(q) is None:
          raise ValueError(f"Surface25u: qubit {q} was not initialized")
        qubits,_ = qmap[q]
        if op.name == OpName.I:
          pass
        elif op.name == OpName.X:
          acc.append(FTOps([FTPrim(op.name, [qubits[1], qubits[6], qubits[11]])]))
        elif op.name == OpName.Z:
          acc.append(FTOps([FTPrim(op.name, [qubits[5], qubits[6], qubits[7]])]))
        else:
          raise ValueError(f"Surface25u: Unsupported logical operation: {op}")
        acc.append(self._error_correction_cycle(q, layers0[q]))
    else:
      raise ValueError(f"Surface25u: Unsupported operation: {op}")

    return reduce(FTComp, acc)
# }}}


