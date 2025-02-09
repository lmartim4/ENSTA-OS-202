#include <algorithm>
#include <cassert>
#include <iostream>
#include <thread>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include "ProdMatMat.hpp"

namespace
{
  constexpr bool DEBUG = true;

  // Função que realiza a multiplicação de um sub-bloco
  void prodSubBlocks(int iRowBlkA, int iColBlkB, int iColBlkA, int szBlock,
                     const Matrix &A, const Matrix &B, Matrix &C)
  {
    // std::cout << "prodSubBlocks called with: iRowBlkA=" << iRowBlkA << ", iColBlkB=" << iColBlkB << ", iColBlkA=" << iColBlkA << ", szBlock=" << szBlock << std::endl; // Print input values

    int rowEnd = std::min(A.nbRows, iRowBlkA + szBlock);
    int colBEnd = std::min(B.nbCols, iColBlkB + szBlock);
    int colAEnd = std::min(A.nbCols, iColBlkA + szBlock);

#pragma omp critical
    {
      // std::cout << "Running colB(" << iColBlkB << "=>" << colBEnd<< ")\t colA("<< iColBlkA << "=>" <<colAEnd<<")\t row(" << iRowBlkA << "=>" << rowEnd << ")" <<std::endl;
    }

    for (int j = iColBlkB; j < colBEnd; ++j)
      for (int k = iColBlkA; k < colAEnd; ++k)
        for (int i = iRowBlkA; i < rowEnd; ++i)
        {
          double a_ik = A(i, k);
          double b_kj = B(k, j);

          // Print the multiplication formula and result
          // std::cout << "C(" << i << ", " << j << ") += A(" << i << "," << k << ")*B(" << k << "," << j << ")" << std::endl;

          C(i, j) += a_ik * b_kj;
        }

    // std::cout << "prodSubBlocks finished." << std::endl; // Indicate function completion
  }

  const int szBlock = 1024;
} // namespace

#define PARALLEL

#ifdef PARALLEL
Matrix operator*(const Matrix &A, const Matrix &B)
{
  assert(A.nbCols == B.nbRows);
  Matrix C(A.nbRows, B.nbCols, 0.0);

  // #pragma omp parallel
  //{
  // #pragma omp for collapse(2) schedule(dynamic)
  for (int iRowBlkA = 0; iRowBlkA < A.nbRows; iRowBlkA += szBlock)
  {
    for (int iColBlkB = 0; iColBlkB < B.nbCols; iColBlkB += szBlock)
    {
      for (int iColBlkA = 0; iColBlkA < A.nbCols; iColBlkA += szBlock)
      {
        prodSubBlocks(iRowBlkA, iColBlkB, iColBlkA, szBlock, A, B, C);
      }
    }
  }
  //}

  return C;
}

#else
Matrix operator*(const Matrix &A, const Matrix &B)
{
  Matrix C(A.nbRows, B.nbCols, 0.0);
  prodSubBlocks(0, 0, 0, std::max({A.nbRows, B.nbCols, A.nbCols}), A, B, C);
  return C;
}

#endif