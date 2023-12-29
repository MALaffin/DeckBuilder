//installed gcc 12 but misssing cc1plus
//apt install g++
//seems to be g++-11 so switching to that
//Include path needed to add /usr/include/c++/11/**
//#pragma managed
//using namespace System;

#include "Model.hpp"
#include "SVMLike1.hpp"
#include <string>

#include <iostream>
int main(){
    std::cout<<"test purposes only\r\n";
    string err;
    err=string(Model::unitTests(0));
    if(!err.empty())
        std::cout<<err<<"\r\n";
    err=string(SVMLike1::unitTests(0));
    if(!err.empty())
        std::cout<<err<<"\r\n";
    return 0;
}