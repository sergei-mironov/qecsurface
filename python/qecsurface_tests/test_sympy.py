import pytest
import pytest
import numpy as np
from sympy import Matrix, tensorproduct
from numpy.testing import assert_allclose

from qecsurface import *

def test_to_sympy():
  circuit = FTOps([
    FTPrim(OpName.X, [1,2]),     # Apply X on qubit 0
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

