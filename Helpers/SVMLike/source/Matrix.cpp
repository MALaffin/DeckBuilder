#include "Matrix.hpp"
#include <cmath>
#include <exception>
#include <cstdlib>
using namespace std;

//statics
Logging<Matrix> Matrix::s_logger=Logging<Matrix>();
const double Matrix::zero=1e-12;//aproximation for rounding

Matrix::Matrix(){
    sizes.resize(2);
    s_logger.addTrackedObject(this);
}
Matrix::~Matrix(){
    s_logger.removeTrackedObject(this,false);
}

Matrix::Matrix(const Matrix * A){
    data=A->data;
    sizes=A->sizes;
    s_logger.addTrackedObject(this);
}
Matrix::Matrix(size_t rows, size_t cols, double values, bool isDiag){
    sizes.resize(2);
    sizes[0]=rows;
    sizes[1]=cols;
    data.resize(rows*cols);
    if(values!=0){
        for(size_t col=0;col<cols;col++){
            if(isDiag & col<rows)
                (*this)(col,col)=values;
            else{
                for(size_t row=0;row<rows;row++)
                    (*this)(row,col)=values;
            }        
        }
    }
    s_logger.addTrackedObject(this);
}

const char * Matrix::set(reals a, dims s){
    if(s.size()!=2)//todo: consider suporting more dimensions
        return s_logger.setStatus("unsuported number of dimentions",__FUNCTION__);
    if(s[0]*s[1]!=a.size())
        return s_logger.setStatus("number of elements inconsistant with dimentions",__FUNCTION__);
    data=a;
    sizes=s;
    return NULL;
}

const char * Matrix::addEquals(const Matrix* B){
    if(sizes[0]!=B->sizes[0] || sizes[1]!=B->sizes[1]
     || sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    //todo: parallelize this
    for(size_t ind=0;ind<data.size();ind++)
        data[ind]+=B->data[ind];
    return NULL;
}

const char * Matrix::add(const Matrix* A,const Matrix* B, Matrix* C){
    C= new Matrix();
    if(A->sizes[0]!=B->sizes[0] || A->sizes[1]!=B->sizes[1]
     || A->sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    //todo: parallelize this
    C->sizes=A->sizes;
    C->data.resize(A->data.size());
    for(size_t ind=0;ind<A->data.size();ind++)
        C->data[ind]=A->data[ind]+B->data[ind];
    return NULL;
}

const char * Matrix::transpose(const Matrix* A, Matrix* At){
    At= new Matrix();
    if(A->sizes.size()!=2 || A->sizes[0]==0)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    
    At->sizes.resize(2);
    size_t rowsA=A->sizes[0];
    size_t colsA=A->sizes[1];
    size_t N=A->data.size();
    size_t Nm1=N-1;
    At->sizes[1]=rowsA;
    At->sizes[0]=colsA;
    At->data.resize(N);
    //todo: parallelize this
    //indA=rowA+colA*rowsA
    //rowA=indA%rowsA
    //colA=indA/rowsA
    //indB=rowB+colB*rowsB
    //indB=colA+rowA*colsA
    size_t indAstart=0;//for(size_t indAstart=0;indAstart<1;indAstart++)
    //size_t rowA=indAstart%rowsA;
    //size_t colA=indAstart/rowsA;
    size_t indB=0;//colA+rowA*colsA;
    for(size_t indA=indAstart;indA<A->data.size();indA++){        
        At->data[indB]=A->data[indA];
        indB+=colsA;
        indB=indB>N?indB-Nm1:indB;      
    }
    return NULL;
}

const char * Matrix::concantenateRows(const Matrix* A,const Matrix* B, Matrix* C){
    C= new Matrix();
    if(A->sizes[1]!=B->sizes[1]
     || A->sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    C->data.resize(A->data.size()+B->data.size());
    C->sizes=A->sizes;
    C->sizes[0]+=B->sizes[0];
    //todo: use memcopy
    for(size_t indA=0;indA<A->sizes[0];indA++)
        C->data[indA]=A->data[indA];
    size_t indC=A->sizes[0];
    for(size_t indB=0;indB<B->sizes[0];indB++){
        C->data[indC]=B->data[indB];
        indC++;
    }
    return NULL;
}

const char * Matrix::concantenateCols(const Matrix* A,const Matrix* B, Matrix* C){
    C= new Matrix();
    if(A->sizes[0]!=B->sizes[0]
     || A->sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    C->data.resize(A->data.size()+B->data.size());
    C->sizes=A->sizes;
    C->sizes[1]+=B->sizes[1];
    //todo: use memcopy
    size_t indA=0;
    size_t indB=0;
    size_t indC=0;
    for(size_t rowA=0;rowA<A->sizes[0];rowA++){
        for(;indA<A->sizes[1];indA++){
            C->data[indC]=A->data[indA];
            indC++;
        }
        for(;indB<B->sizes[1];indB++){
            C->data[indC]=B->data[indB];
            indC++;
        }
    }
    return NULL;
}

const char * Matrix::selectCols(size_t colL,size_t colHp1, Matrix* B) const{
    B= new Matrix();
    if(colL<colHp1 || colHp1>sizes[0]
     || sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    B->data.resize((colHp1-colL)*sizes[1]);
    B->sizes=sizes;
    B->sizes[0]=(colHp1-colL);
    //todo: use memcopy
    size_t indA=0;
    size_t indB=0;
    for(size_t rowA=colL;rowA<colHp1;rowA++){//todo: consider colHp1
        for(size_t rowA;rowA<sizes[1];rowA++){
            B->data[indB]=data[indA];
            indB++;
            indA++;
        }
    }
    return NULL;
}

double & Matrix::operator()(size_t r,size_t c){
    if(sizes[0]<r || sizes[1]<c)
        throw s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    return data[r+sizes[0]*c];
}
const char * Matrix::selectRows(size_t rowL,size_t rowHp1, Matrix* B) const{
    B= new Matrix();
    if(rowL<rowHp1 || rowHp1>sizes[1]
     || sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    B->data.resize((rowHp1-rowL)*sizes[0]);
    B->sizes=sizes;
    B->sizes[0]=(rowHp1-rowL);
    //todo: use memcopy
    size_t indA=sizes[0]*rowL;
    size_t skip=sizes[1]-(rowHp1-rowL);
    size_t indB=0;
    for(size_t colA=0;colA<sizes[1];colA++){//todo: consider rowHp1
        for(size_t rowA=rowL;rowA<rowHp1;rowA++){
            B->data[indB]=data[indA];
            indB++;
            indA++;
        }
        indA+=skip;
    }
    return NULL;
}

const char * Matrix::elementMultiply(const Matrix* A, const Matrix* B, Matrix * C){
    C= new Matrix();
    if(A->sizes[0]!=B->sizes[0] || A->sizes[1]!=B->sizes[1]
     || A->sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    //todo: parallelize this
    C->sizes=A->sizes;
    C->data.resize(A->data.size());
    for(size_t ind=0;ind<A->data.size();ind++)
        C->data[ind]=A->data[ind]*B->data[ind];
    return NULL;
}
const char * Matrix::sum(double& s){
    //todo: parallelize this
    s=0;
    for(size_t ind=0;ind<data.size();ind++)
        s+=data[ind];
    return NULL;
}

const char * Matrix::multiply(const Matrix* A, const Matrix* B, Matrix * C){
    if(A->sizes[1]!=B->sizes[0]
     || A->sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    C=new Matrix();
    C->sizes[0]=A->sizes[0];
    C->sizes[1]=B->sizes[1];
    C->data.resize(C->sizes[0]*C->sizes[1]);
    for(size_t row=0;row<A->sizes[1];row++){
        Matrix * rowVector;
        const char * err = A->selectRows(row,row,rowVector);
        if(err)
            return s_logger.setStatus("'"+string(err) +"' cant make row-Vector",__FUNCTION__);
        for(size_t col=0;col<B->sizes[1];col++){
            size_t indC=row+col*C->sizes[0];
            size_t indB=col*B->sizes[0];
            C->data[indC]=0;
            for(size_t inner=0;inner<B->sizes[0];inner++){
                C->data[indC]+=rowVector->data[inner]*B->data[indB];
                indB++;
            }
        }
    }
    return NULL;
}
const char * Matrix::leftMultiplyEqual(const Matrix* A){
    if(A->sizes[1]!=sizes[0]
     || A->sizes.size()!=2 || sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    Matrix * C=new Matrix();
    C->sizes[0]=A->sizes[0];
    C->sizes[1]=sizes[1];
    C->data.resize(C->sizes[0]*C->sizes[1]);
    for(size_t row=0;row<A->sizes[1];row++){
        Matrix * rowVector;
        const char * err = A->selectRows(row,row,rowVector);
        if(err)
            return s_logger.setStatus("'"+string(err) +"' cant make row-Vector",__FUNCTION__);
        for(size_t col=0;col<sizes[1];col++){
            size_t indC=row+col*C->sizes[0];
            size_t indB=col*sizes[0];
            C->data[indC]=0;
            for(size_t inner=0;inner<sizes[0];inner++){
                C->data[indC]+=rowVector->data[inner]*data[indB];
                indB++;
            }
        }
    }
    data=C->data;
    delete C;
    return NULL;
}


const char * Matrix::rightMultiplyEqual(const Matrix* B){
    if(sizes[1]!=B->sizes[0]
     || sizes.size()!=2 || B->sizes.size()!=2)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    Matrix * C=new Matrix();
    C->sizes[0]=sizes[0];
    C->sizes[1]=B->sizes[1];
    C->data.resize(C->sizes[0]*C->sizes[1]);
    for(size_t row=0;row<sizes[1];row++){
        Matrix * rowVector;
        const char * err = this->selectRows(row,row,rowVector);
        if(err)
            return s_logger.setStatus("'"+string(err) +"' cant make row-Vector",__FUNCTION__);
        for(size_t col=0;col<B->sizes[1];col++){
            size_t indC=row+col*C->sizes[0];
            size_t indB=col*sizes[0];
            C->data[indC]=0;
            for(size_t inner=0;inner<B->sizes[0];inner++){
                C->data[indC]+=rowVector->data[inner]*B->data[indB];
                indB++;
            }
        }
    }
    data=C->data;
    delete C;
    return NULL;
}

const char * Matrix::multColEq(Matrix* A,size_t col,double scale){
    size_t rows=A->sizes[0];
    if(col>A->sizes[1])
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    for(size_t ind=col*rows;ind<(1+col)*rows;ind++)
        A->data[ind]*=scale;
    return NULL;
}
const char * Matrix::addScaledColBtoColCEq(Matrix* A,size_t colB,size_t colC,double scale){
    size_t rows=A->sizes[0];
    if(colB>=A->sizes[1] || colC>=A->sizes[1])
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    size_t indB=colB*rows;
    for(size_t indC=colC*rows;indC<(1+colC)*rows;indC++,indB++)
        A->data[indC]+=scale*A->data[indB];
    return NULL;
}
const char * Matrix::swapColBandColCEq(Matrix* A,size_t colB,size_t colC){
    size_t rows=A->sizes[0];
    if(colB>=A->sizes[1] || colC>=A->sizes[1])
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    size_t indB=colB*rows;
    for(size_t indC=colC*rows;indC<(1+colC)*rows;indC++,indB++){
        double tmp=A->data[indC];
        A->data[indC]=A->data[indB];
        A->data[indB]=tmp;
    }
    return NULL;
}

const char * Matrix::gaussianElimination(const Matrix* M,Matrix* R,bool columnEchelon){
    //~2N^2 flops
    if(M->sizes[0] < M->sizes[1])//need more cols than rows to make sense
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    const char * err;
    if(!columnEchelon){
        Matrix* T;
        err=Matrix::transpose(M,T);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        R=T;
    }else
        R=new Matrix(M);
    
    //triangular form, with sorting for larger diagonal values
    size_t rows=M->sizes[0];
    size_t cols=M->sizes[1];
    for(size_t colB=0;colB<cols;colB++){
        for(size_t colC=colC+1;colC<cols;colC++){
            double vB=(*R)(colB,colB);
            double vC=(*R)(colB,colC);
            if(std::fabs(vB)>std::fabs(vC)){//note vB can not be zero
                err=addScaledColBtoColCEq(R,colB,colC,-vC/vB);
                if(err)
                    return s_logger.setStatus(err,__FUNCTION__);
            }else{
                if(vC!=0)
                    err=swapColBandColCEq(R,colB,colC);
                    if(err)
                        return s_logger.setStatus(err,__FUNCTION__);
            }
        }
    }//~N(N+1)mulitplies+N(N+1)additions
    //form a triangular matrix first
    for(size_t colB=0;colB<cols;colB++){
        for(size_t colC=0;colC<cols;colC++){
            double vB=(*R)(colB,colB);
            if(colB==colC){
                if(vB!=0){
                    err=multColEq(R,colB,1/vB);
                    if(err)
                        return s_logger.setStatus(err,__FUNCTION__);
                }
                continue;
            }
            double vC=(*R)(colB,colC);
            if(vB!=0 && vC!=0){
                err=addScaledColBtoColCEq(R,colB,colC,-vC/vB);
                if(err)
                    return s_logger.setStatus(err,__FUNCTION__);
            }
        }
    }//~N^2 mulitplies

    if(!columnEchelon){
        Matrix* T;
        err=Matrix::transpose(R,T);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        delete R;
        R=T;
    }
    return NULL;
}

//need row operations
//need gausianElimination
const char * Matrix::inverseByGE(const Matrix* A, Matrix * Ai){
    //https://en.wikipedia.org/wiki/Gaussian_elimination
    //right side of gausianElimination([A I],rowEchelon)
    if(A->sizes[1]!=A->sizes[0])
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    Matrix I(A->sizes[0],A->sizes[1],1,true);
    Matrix * AI;
    const char * err=concantenateCols(A,&I,AI);
    if(err)
        return s_logger.setStatus(err,__FUNCTION__);
    Matrix * IAi;
    err=gaussianElimination(AI,IAi,true);
    delete AI;
    if(err)
        return s_logger.setStatus(err,__FUNCTION__);
    err=IAi->selectCols(A->sizes[0],IAi->sizes[1],Ai);
    delete IAi;
    if(err)
        return s_logger.setStatus(err,__FUNCTION__);
    return NULL;
}

const char * Matrix::QR(const Matrix* A, Matrix* Q, Matrix* R){
    Q=new Matrix(A);
    size_t rows=A->sizes[0];
    size_t cols=A->sizes[1];
    if(rows!=cols)
        return s_logger.setStatus("mismatched dimentions",__FUNCTION__);
    size_t colInd=0;
    for(size_t col=0;col<cols;col++){ 
        double au=0;
        double uu=0;
        size_t ind=colInd;
        for(size_t row=0;row<rows;row++){
            double ui=Q->data[ind];
            double ai=A->data[ind];
            au+=ai*ui;
            uu+=ui*ui;
            ind++;
        }//8N^2
        double adu=au/uu;
        size_t col2Ind=0;
        for(size_t col2=0;col2<col;col2++){
            ind=colInd;
            size_t ind2=col2Ind;
            for(size_t row=0;row<rows;row++){
                Q->data[ind2]-=adu*Q->data[ind];
                ind++;
                ind2++;
            }
            col2Ind+=rows;
        }//7N^3/2
        ind=colInd;
        for(size_t row=0;row<rows;row++){
            Q->data[ind]/=uu;
            ind++;
        }//3N^2
        colInd+=rows;
    }
    R=new Matrix(rows,cols,0,false);
    colInd=0;

    for(size_t col=0;col<cols;col++){
        size_t rowInd=0;
        for(size_t row=0;row<rows;row++){
            double ae=0;
            size_t ind=colInd;
            size_t ind2=rowInd;
            for(size_t row2=0;row2<rows;row2++){
                double ei=Q->data[ind2];
                double ai=A->data[ind];
                ae+=ai*ei;
                ind++;
                ind2++;
            }//7N^3/2
            (*R)(row,col)=ae;
            rowInd+=rows;
        }
        colInd+=rows;
    }
    return NULL;
}//~7N^3+11N^2

const char * Matrix::eigenByQR(const Matrix* M, Matrix* values, Matrix* vector){

    // QR method from https://en.wikipedia.org/wiki/QR_algorithm
    // Qn Rn = An by https://en.wikipedia.org/wiki/QR_decomposition#Computing_the_QR_decomposition
    // Anp1=Rn Qn is similar to An and has identical eigen values e.
    // An converges to a triangle (schur form) with eigen values on diagonal
    // right side of gaussianElimination([A-eI],rowEchelon) to get vectors 
    // O(N^2?*S) multipplies every iteration
    const char * err;
    Matrix* A=new Matrix(M);
    size_t maxS=3;
    for(size_t s=0;s<maxS;s++){
        Matrix* Q;
        Matrix* R;
        err=QR(A, Q, R);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        delete A;
        err=multiply(R, Q, A);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        delete Q;//could return this if M is symetric
        delete R;
    }//~(7N^3+11N^2)*maxS

    values=A;
    size_t cols=M->sizes[1];
    vector=new Matrix(cols,cols,0.0,false);
    
    //for diagonal matrix
    size_t rank=0;
    size_t colsToCheck=M->sizes[1]<M->sizes[0]?M->sizes[1]:M->sizes[0];
    size_t addedCols=0;
    for(size_t e=0;e<colsToCheck;e++){
        double val=(*A)(e,e);
        if(fabs(val)>zero){
            rank++;
            Matrix* MmeI=new Matrix(M);
            Matrix* meI=new Matrix(M->sizes[0],M->sizes[0],-val,true);
            err=MmeI->addEquals(meI);
            delete meI;
            if(err){
                delete MmeI;
                return s_logger.setStatus(err,__FUNCTION__);
            }
            Matrix* R;
            err=gaussianElimination(MmeI,R,false);
            delete MmeI;
            if(err)
                return s_logger.setStatus(err,__FUNCTION__);
            for(size_t s=0;s<cols;s++){
                if(fabs((*R)(s,s))<zero){
                    double w=0;
                    for(size_t row=0;row<cols;row++){
                        (*vector)(row,addedCols)=(*R)(row,s);
                        w+=(*R)(row,s)*(*R)(row,s);
                    }
                    w=sqrt(w);
                    for(size_t row=0;row<cols;row++)
                        (*vector)(row,addedCols)/=w;
                    addedCols++;
                    if(addedCols>cols)
                        break;
                }
            }
            delete R;
            if(addedCols>cols)
                return s_logger.setStatus("repeated roots found",__FUNCTION__);
        }
    }
    return NULL;
}

const char * Matrix::norm(double& s){
    //todo: parallelize this
    if(sizes[0]!=0&&sizes[1]!=0&&sizes.size())
        s_logger.setStatus("unsuported for norm",__FUNCTION__);
    long double ls=0;
    for(size_t ind=0;ind<data.size();ind++)
        ls+=data[ind]*data[ind];
    s=(double)sqrt(ls);
    return NULL;
}

const char * Matrix::eigenByPower(const Matrix* A, Matrix* values, Matrix* vector){
    
    //power method from https://en.wikipedia.org/wiki/Eigendecomposition_of_a_matrix    
    //  (A^n v)/|A^n v|=q_n v is seeded randomly and q_n almost always converges to an eigen vector for biggest eigen value
    //  Av=ev so |Av|/|v|=e
    //  note by assosiative property A^(2^m)=A^(2^(m-1))*A^(2^(m-1))
    //let A=MM^t so A is hermitian ... https://users.cs.duke.edu/~kamesh/CPS294-PDF/Lecture5.pdf
    //  (1) Theorem 1: for Av=ev v are orthogonal and e and v are real
    //given A v_n=e_n v_n (seeded by power method for n=1)
    //let [v_1..v_n]^t x = 0; need basis of V_n = [v_1..v_n]^t so x=B_n y (B_n is Nxn y is nx1)
    //  https://en.wikipedia.org/wiki/Kernel_(linear_algebra)
    //  B_n=non pivots of bottom of gausianElimination([V_n;I_N],colEchelon)
    //  rank analysis leads to basis B_n being Nxn but not sure about numeric noise
    //consider A B_n y=e B_n y
    //  B_n^t A B_n y=e B_n^t B_n y
    //  B_n^t B_n is Hermitian so well behaved eigen values in N-n.
    //   so let B_n^t B_n = VB_n^t EB_n VB_n
    //   B_n^t A B_n y=e VB_n^t EB_n VB_n y
    //   orthonormal VB_n so 
    //  VB_n B_n^t A B_n VB_n^t y=e EB_n y
    //  let v_np1 = B_n y = root(EB_n) VB_n y
    //   if EB_n elements are negative, then v_np1 would be complex which is contridicted by (1)
    //   so we can take root of EB_n and
    //  sqrt(1/EB_n) VB_n B_n^t A B_n VB_n^t sqrt(1/EB_n)^t y=e y
    //  let A_n = sqrt(1/EB_n) VB_n B_n^t A B_n VB_n^t sqrt(1/EB_n)^t 
    //  A_n y =e y has the same eigen value as A x e x and eigen vector B_n y = x by construction
    //  A_n is still hermitian an so us power method on it to find a stable e and y
    //back at the top level, let e_np1=e and v_np1 = B_n y 
    //v_np1 is orthogonal to all v_n by construction so we found another vector with the trusted power method
    //repeat until B_n is empty (V_n rank is N) 
    // Ugg... ? O(N^3?*log(S)) ?

    const char * err;
    //todo: consider adding symetry options to matrixes and veifying input is symetric

    size_t rows=A->sizes[0];//used a lot here
    //SN^2 vs S^.5*N^3
    //hoping for small S...
    Matrix v(rows,1,0.0,false);//will store as column vector
    size_t maxS=3;
    //fill up an eigen vector v using power method for symetric M
    {
        srand(rows);//repeatable
        for(size_t row;row<rows;row++){
            v(row,1)=rand();
        }
        for(size_t s=0;s<maxS;s++){
            v.leftMultiplyEqual(A);
            //consider normalizing here in it becomes numerically unstable
        }    
    }
    double scale;
    err=v.norm(scale);
    if(err)
        return s_logger.setStatus(err,__FUNCTION__);
    for(size_t row;row<rows;row++){
        v(row,1)/=scale;
    }
    
    //estimate eigen value (and transpose v for constraint later)
    double e;
    {
        Matrix* vest;
        err=multiply(A,&v,vest);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        v.sizes[0]=rows;
        v.sizes[1]=rows;
        err=multiply(&v,vest,vest);
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);
        e=vest->data[0];
    }
    
    //B_n=non pivots of bottom of gausianElimination([V_n;I_N],colEchelon)
    //surely something more efficient exists...
    Matrix * B_n;// (right- (N-1) to N basis for orthoganality constraint nullspace)
    {
        Matrix orhogonalConstraint(rows-1,rows-1,0.0,false);
        Matrix forKernalFind(rows+1,rows,1.0,true);
        for(size_t row;row<rows;row++){
            forKernalFind(rows,row)=v(0,row);
        }
        Matrix* containsKernal;
        err=gaussianElimination(&forKernalFind,containsKernal,true);
        if(err) return s_logger.setStatus(err,__FUNCTION__);
        err=containsKernal->selectCols(1,rows,B_n);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        delete containsKernal;
        containsKernal=B_n;
        err=containsKernal->selectRows(1,rows,B_n);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        delete containsKernal;
    }

    //sqrt(1/EB_n) VB_n B_n^t A B_n VB_n^t sqrt(1/EB_n)^t y=e y

    Matrix * B_nt;//used a few times
    err=transpose(B_n,B_nt);
    if(err) 
        return s_logger.setStatus(err,__FUNCTION__);

    Matrix* subValues;
    Matrix* subVectors;
    //get sub eigen problem from M and B_n
    {
        //make tansformation parameters from B_n
        Matrix* VB_n;
        Matrix* rootEB_n;
        {
            Matrix * B_ntB_n = new Matrix(B_nt);
            err=B_ntB_n->rightMultiplyEqual(B_n);
            if(err) 
                return s_logger.setStatus(err,__FUNCTION__);
            err=eigenByPower(B_ntB_n, rootEB_n, VB_n);
            delete B_ntB_n;
            if(err)
                return s_logger.setStatus(err,__FUNCTION__);

            for(size_t row=0;row<rows;row++){
                double val=(*rootEB_n)(row,row);
                if(val<zero)
                    return s_logger.setStatus("invalid value",__FUNCTION__); 
                (*rootEB_n)(row,row)=sqrt(val);
            }   
        }
        Matrix * subM=new Matrix(rootEB_n);
        subM->rightMultiplyEqual(VB_n);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        subM->rightMultiplyEqual(VB_n);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        err=subM->rightMultiplyEqual(B_nt);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        err=subM->rightMultiplyEqual(A);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        err=subM->rightMultiplyEqual(B_n);
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        Matrix * VB_nt;
        {
            err=transpose(VB_n,VB_nt);
            if(err) 
                return s_logger.setStatus(err,__FUNCTION__);
        }
        err=subM->rightMultiplyEqual(VB_nt);
        delete VB_nt;
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        err=subM->rightMultiplyEqual(rootEB_n);//rootEB_n=transpose(rootEB_n)
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
        Matrix* subVectors_y;
        err=eigenByPower(subM, subValues, subVectors_y);
        delete subM;
        if(err)
            return s_logger.setStatus(err,__FUNCTION__);

        //eigen values fine, vectors need transformation
        err=multiply(B_n,subVectors_y,subVectors);
        delete subVectors_y;
        if(err) 
            return s_logger.setStatus(err,__FUNCTION__);
    }
    

    //map values to ouptut
    values=new Matrix(rows,rows,0.0,false);
    (*values)(0,0)=e;
    size_t rowm1=0;
    for(size_t row=1;row<rows;row++){
        (*values)(row,row)=(*subValues)(rowm1,rowm1);
        rowm1++;
    }

    //map vector to outputs
    vector=new Matrix(rows,rows,0.0,false);
    for(size_t row=0;row<rows;row++){
        (*vector)(row,0)=v(0,row);
        for(size_t col=1;col<rows;col++)
            (*vector)(row,col)=(*subVectors)(row,col-1);
    }
    delete subValues;
    delete subVectors;
    return NULL;
}

const char * Matrix::unitTests(){
    
    return NULL;
}