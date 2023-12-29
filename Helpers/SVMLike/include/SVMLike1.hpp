#pragma once
#include "Model.hpp"

class PORT SVMLike1:Model{
    public:
        SVMLike1();//actual ctor
        ~SVMLike1();//actual dtor
        PORT static const char * makeModel(Model* p_this);//allocator
        PORT static const char * unitTests(int test);
    private:
        //basic modeling Operations 
        const char * train(
            const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT);
        const char * test(
            const size_t p_T, const real* p_data_IxT
        , real* p_estimate_OxT)const;
};