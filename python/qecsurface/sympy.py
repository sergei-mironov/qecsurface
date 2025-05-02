# The function defined below converts an FTCircuit containing FTPrim operations into a unitary
# matrix using Sympy.  Operation-specific matrices for X, Z, and H gates are constructed and
# sequentially applied to the identity matrix to form the complete circuit unitary matrix. The
# function handles both FTOps and composite FTComp circuits, focusing specifically on FTPrim
# operations.

from sympy import Matrix, eye, zeros, tensorproduct
from sympy.physics.quantum import Dagger
from functools import reduce

from qecsurface.type import *

def to_sympy[Q](circuit: FTCircuit[Q]) -> Matrix:
  """ Convert FTCircuit into a unitary matrix in Sympy. Only handles FTPrim operations. """

  num_qubits = max(labels(circuit))+1

  def _traverse_op(op: FTOp[Q], acc) -> Matrix:

    if isinstance(op, FTPrim):
      local_matrix = eye(2)  # Default for "I" operation
      if op.name == OpName.X:
        local_matrix = Matrix([[0, 1], [1, 0]])  # Pauli X gate
      elif op.name == OpName.Z:
        local_matrix = Matrix([[1, 0], [0, -1]])  # Pauli Z gate
      elif op.name == OpName.H:
        local_matrix = (1 / 2**0.5) * Matrix([[1, 1], [1, -1]])  # Hadamard gate

      matrix_list = []
      for i in range(num_qubits):
        if i in op.qubits:
          matrix_list.append(local_matrix)  # Use local operation for targeted qubits
        else:
          matrix_list.append(eye(2))  # Use identity otherwise

      full_matrix = reduce(lambda a, b: tensorproduct(a, b), matrix_list)

      # By using `tensorproduct`, you should avoid the AttributeError associated with
      # the `MutableDenseMatrix` object when trying to use an undefined `kron` method.

    else:
      raise ValueError(f"Unsupported operation in traverse_ftcircuit_to_sympy: {op}")

    acc.append(full_matrix)
    return acc

  ops = traverse_circuit(circuit, _traverse_op, [])
  return reduce(lambda a, b: a * b, ops)  # Ensure matrix multiplication for the final unitary


def build_check_matrix(stabilizers, zero_labels=None):
  zero_labels = zero_labels or set()
  # Initialize a zero matrix with dimensions (num_stabilizers, 2 * num_unique_labels)
  unique_labels = set(label for op in stabilizers for label in op.qubits) | set(zero_labels)
  num_stabilizers = len(stabilizers)
  num_unique_labels = len(unique_labels)

  # Map qubit labels to matrix column indices
  label_to_index = {label: idx for idx, label in enumerate(sorted(unique_labels))}

  check_matrix = zeros(num_stabilizers, 2 * num_unique_labels)

  for i, op in enumerate(stabilizers):
    if isinstance(op, FTPrim):
      if op.name == OpName.X:
        for q in op.qubits:
          col_index = label_to_index[q]
          check_matrix[i, col_index] = 1  # Set X part
      elif op.name == OpName.Z:
        for q in op.qubits:
          col_index = label_to_index[q] + num_unique_labels
          check_matrix[i, col_index] = 1  # Set Z part

  return check_matrix

