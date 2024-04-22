#pragma once
#include<vector>
#include<string>
#include "Logging.hpp"
typedef std::vector<double> reals;
typedef std::vector<size_t> dims;
class Matrix{
    public:
        //todo: streamline interfaces; likely mirror static interfaces for objects
        Matrix();
        ~Matrix();
        Matrix(const Matrix * A);
        Matrix(size_t rows, size_t cols, double values, bool isDiag);
        const char * set(reals a, dims s);
        const char * addEquals(const Matrix* B);
        static const char * add(const Matrix* A,const Matrix* B, Matrix* C);
        static const char * transpose(const Matrix* A, Matrix* At);
        static const char * concantenateRows(const Matrix* A,const Matrix* B, Matrix* C);
        static const char * concantenateCols(const Matrix* A,const Matrix* B, Matrix* C);
        const char * selectRows(size_t ro1L,size_t rowHp1, Matrix* B) const;
        const char * selectCols(size_t colL,size_t colHp1, Matrix* B) const;
        static const char * elementMultiply(const Matrix* A, const Matrix* B, Matrix * C);
        const char * sum(double& s);
        const char * norm(double& s);
        static const char * multiply(const Matrix* A, const Matrix* B, Matrix * C);
        const char * leftMultiplyEqual(const Matrix* A);
        const char * rightMultiplyEqual(const Matrix* A);
        static const char * inverseByGE(const Matrix* A, Matrix * Ai);//Gaussian Elimination based
        static const char * eigenByQR(const Matrix* A, Matrix* values, Matrix * vector);//
        static const char * eigenByPower(const Matrix* A, Matrix* values, Matrix * vector);//for symetric A
        const char * unitTests();
    private:
        static Logging<Matrix> s_logger;
        //todo: not managing memory leaks on error conditions, consider use logger to clear
        reals data;
        dims sizes;
        //indexing scheme:
        //rows=sizes[0];
        //cols=sizes[1];
        //ind=row+col*rows
        static const char * multColEq(Matrix* A,size_t col,double scale);
        static const char * gaussianElimination(const Matrix* M,Matrix* R,bool columnEchelon);
        static const char * addScaledColBtoColCEq(Matrix* A,size_t colB,size_t colC,double scale);
        static const char * swapColBandColCEq(Matrix* A,size_t colB,size_t colC);
        static const char * QR(const Matrix* A, Matrix* Q, Matrix* R);
        //following will throw const char * on error
        double & operator()(size_t r,size_t c);     
        
        static const double zero;//aproximation for rounding  
};
