#include "SVMLike1.hpp"
typedef unsigned int dims;


SVMLike1::SVMLike1()/*:Model()*/{

}
SVMLike1::~SVMLike1(){

}
const char * SVMLike1::makeModel(Model*& p_this){
    p_this = new SVMLike1();
    return NULL;
}
const char * SVMLike1::unitTests(int test){
    const char * err;
    Model* test1;
    err=makeModel(test1);
    if(err)
        return setStatus("svmlike1 make",__FUNCTION__);
    
    vector<real> inputs{0.0, 0.5, 1.0};
    vector<real> outputs{1.0, 0.0, 1.0};//4x^2-4x+1
    err=Model::train(test1,inputs.size(),&inputs[0],&outputs[0]);
    if(err)
        return setStatus("svmlike1 train",__FUNCTION__);

    vector<real> inputs2{0.25, 0.75};
    vector<real> outputs2{0.25, 0.25};
    vector<real> estimate2(outputs2.size());
    err=Model::test(test1, inputs.size(),&inputs2[0],&estimate2[0]);
    if(err)
        return setStatus("svmlike1 test",__FUNCTION__);

    return NULL;
}

const char * SVMLike1::train(const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT){
    return "derived train not implemented";
}
const char * SVMLike1::test(const size_t p_T, const real* p_data_IxT 
, real* p_estimate_OxT) const{
    return "derived test not implemented";
}