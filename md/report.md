The problem
-----------

This document contains the solution for the surface code quantum error correction problem. The
project repository is hosted on Github:

https://github.com/sergei-mironov/qecsurface


Your task is to **set up a distance 3 surface code using PennyLane**. If you are not familiar with
Surface Codes, this may be a very useful resource:
[https://arxiv.org/pdf/1404.3747](https://arxiv.org/pdf/1404.3747). Try to simulate **at least one
cycle of the quantum error correction scheme** and give a quick interpretation of the results. Try
**adding some noise to the circuit** (for example, add a random bit-flip in the circuit), and see
what happens to the measurement. You should **describe in words how the decoding would happen**. If
you have the extra time, feel free to also implement some **simple decoding protocols**. The
expected output of this exercise is a Jupyter Notebook. But feel free to deliver your answer in
whichever medium you see fit. Most importantly, try to learn about quantum error correction and give
us an insight into the way you tackle difficult, unseen problems.



Setup
-----


<div class="cell code">
  ```python
  from numpy.testing import assert_allclose
  from qecsurface import *
  ```

  <div class="output stream stdout">
  ```result
  ```
  </div>
</div>


Basic operations
----------------

<div class="cell code">
  ```python
  circuit_ft = FTComp(
    FTOps([
      FTInit(qubit=0, alpha=1.0, beta=0.0),         # Initialize the qubit in a known state
      FTPrim(OpName.H, [1]),                        # Apply Hadamard to qubit 1
      FTCtrl(control=1, op=FTPrim(OpName.X, [2])),  # Entangle qubits 1 and 2
      FTCtrl(control=0, op=FTPrim(OpName.X, [1])),  # Bell state preparation
      FTMeasure(qubit=0, label="m0"),
      FTMeasure(qubit=1, label="m1")
    ]),
    FTComp(
      FTOps([
        FTCond(lambda m: m["m0"] == 1, FTPrim(OpName.X, [2]))  # Conditional X based on m0
      ]),
      FTOps([
        FTCond(lambda m: m["m1"] == 1, FTPrim(OpName.Z, [2]))  # Conditional Z based on m1
      ])
    )
  )
  cPL = to_pennylane_mcm(circuit_ft)
  print(qml.draw(cPL)())
  ```

  <div class="output stream stdout">
  ```result
  0: ──|Ψ⟩────╭●──┤↗│  │0⟩─────────────────┤            
  1: ──H───╭●─╰X───║────────┤↗│  │0⟩───────┤            
  2: ──────╰X──────║─────────║────────X──Z─┤            
                   ╚═════════║════════╩══║═╡  Sample[MCM]
                             ╚═══════════╩═╡  Sample[MCM]
  ```
  </div>
</div>


Bitflip error correction code
-----------------------------


<div class="cell code">
  ```python
  data = [0, 1, 2]
  syndrome = [3, 4]
  cPL = to_pennylane_probs(reduce(FTComp, [
    FTOps([FTInit(0, 1/2, 1/2)]),
    bitflip_encode(0, data),
    FTOps([FTPrim(OpName.X, [1])]), # Introducing an error
    bitflip_detect(data, syndrome),
    bitflip_correct(data),
  ]), data)
  print(qml.draw(cPL)())
  probs = cPL()
  assert_allclose(probs, [0.5, 0.,  0.,  0.,  0.,  0.,  0.,  0.5])
  ```

  <div class="output stream stdout">
  ```result
  0: ──|Ψ⟩─╭●─╭●────╭●───────────────────────────────X───────┤ ╭Probs
  1: ──────╰X─│───X─│──╭●───────────╭●───────────────║──X────┤ ├Probs
  2: ─────────╰X────│──│────────────│──╭●────────────║──║──X─┤ ╰Probs
  3: ───────────────╰X─╰X──┤↗│  │0⟩─│──│─────────────║──║──║─┤      
  4: ───────────────────────║───────╰X─╰X──┤↗│  │0⟩──║──║──║─┤      
                            ╚═══════════════║════════╬══╬══╣        
                                            ╚════════╩══╩══╝        
  ```
  </div>
</div>


Surface25 error correction code
-------------------------------

Surface25 Quantum Error Correction Code[1] (with unified syndrome qubits) error correction
cycle. The error correction routine corrects any single data qubit Pauli error.

The simplifications are as follows: (1) Syndrome qubits are considered to be perfect; (2)
Therefore, Hadamard check circuits are applied to data qubits without a specific order; (3)
Further, to enhance simulation speed, all syndrome qubits are represented using a single qubit
which is re-used after each syndrome measurement.

[1] - https://arxiv.org/pdf/1404.3747

<div class="cell code">
  ```python
  data = list(range(13))
  syndrome = [13]
  error_op, error_qubit = OpName.X, 6
  layer0,layer1,layer2 = 0,1,2
  c1,ml1 = surface25u_detect(data, syndrome, layer0)          # (a)
  err = FTOps([FTPrim(error_op,[error_qubit])])               # (b)
  c2,ml2 = surface25u_detect(data, syndrome, layer1)          # (c)
  corr = surface25u_correct(data, layer0, layer1)             # (d)
  c3,ml3 = surface25u_detect(data, syndrome, layer2)          # (e)
  cPL = to_pennylane_mcm(reduce(FTComp,[c1,err,c2,corr,c3]))  # (f)
  msms = cPL()                                                # (g)
  expected = surface25u_print2(msms, ml1)
  assert all(e not in expected for e in "XZ"), f"Errors in the zero state:\n{expected}"
  synd = surface25u_print2(msms, ml2)
  print("Error syndrome:")
  print(synd)
  assert any(e in synd for e in "XZ"), f"Errors not found in the syndrome:\n{synd}"
  actual = surface25u_print2(msms, ml3)
  assert actual == expected, f"Correction failed:\n{actual}"
  ```

  <div class="output stream stdout">
  ```result
  Error syndrome:

  o   o   o
    o Z o 
  o   o   o
    o Z o 
  o   o   o

  ```
  </div>
</div>




The desired quantum circuit is first defined in a minimalistic EDSL from the `qecsurface.type`
module. Various subcuruit building routines are defined in `qecsurface.qeccs`.  The result is
then lowered to PennyLane and simulated.

Technical details: **(a)** - Initialize the logical-zero state; **(b)** - Introduce a data qubit
error; **(c)** - Define an error detection circuit; **(d)** - Apply corrections using a trivial
decoding protocol; **(e)** - Define the error detection for the second time; **(f)** - Stack the
resulting circuits and convert them to the PennyLane format and **(g)** - Obtain the
mid-circuitmeasurement samples (msms) by running the simulation.

