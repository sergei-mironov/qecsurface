import pytest
import pytest
import numpy as np
from sympy import Matrix, tensorproduct
from numpy.testing import assert_allclose

from qecsurface import *

def test_to_sympy():
  circuit = FTOps([
    FTPrim(OpName.X, [1,2]),
  ])

  result_matrix = to_sympy(circuit)

  X = Matrix([[0, 1], [1, 0]])
  I = Matrix([[1, 0], [0, 1]])
  expected_matrix = tensorproduct(I, X, X)

  # Convert result and expected matrices to numpy arrays
  result_np = np.array(result_matrix.tolist()).astype(np.float64)
  expected_np = np.array(expected_matrix.tolist()).astype(np.float64)

  # Use assert_allclose for comparison with a tolerance for floating point errors
  assert_allclose(result_np, expected_np, atol=1e-8)


def test_check_matrix_example1():
  # Define a simple set of stabilizers for testing
  stabilizers = [
    FTPrim(OpName.X, ['q1', 'q2', 'q4']),
    FTPrim(OpName.Z, ['q1', 'q3']),
    FTPrim(OpName.X, ['q3', 'q4']),
    FTPrim(OpName.Z, ['q2', 'q4'])
  ]

  # Build the check matrix using the function
  check_matrix = build_check_matrix(stabilizers)

  # Convert expected matrix structure assuming sorted labels
  expected_matrix = Matrix([
    [1, 1, 0, 1, 0, 0, 0, 0],  # X(q1, q2, q4)
    [0, 0, 0, 0, 1, 0, 1, 0],  # Z(q1, q3)
    [0, 0, 1, 1, 0, 0, 0, 0],  # X(q3, q4)
    [0, 0, 0, 0, 0, 1, 0, 1]   # Z(q2, q4)
  ])

  assert check_matrix == expected_matrix, "Test failed: Check matrix does not match expected"


def test_check_matrix_degenerate():
  # Define a simple set of stabilizers for testing
  stabilizers = [
    FTPrim(OpName.X, ['q1', 'q2']),
    FTPrim(OpName.X, ['q1', 'q2']),
  ]

  # Build the check matrix using the function
  check_matrix = build_check_matrix(stabilizers)
  print(check_matrix)
  assert check_matrix.rank() == 1

