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
    const char * err;
    err=Model::unitTests(0);
    if(err)
        std::cout<<err<<"\r\n";
    else
        std::cout<<"Model OK\r\n";
    err=SVMLike1::unitTests(0);
    if(err)
        std::cout<<err<<"\r\n";
    else
        std::cout<<"SVMLike1 OK\r\n";
    return 0;
}