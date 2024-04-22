#pragma once
#include "Logging.hpp"
#include <map>
#include <string>
#include <vector>
typedef std::map<std::string,std::vector<double>> NamedValues;
//some other items I expect to use globally
typedef double real;
#if COMPILING
#   define PORT __attribute__((visibility("default")))
#else
#   define PORT
#endif
class PORT Model{
    public:
        Model();//actual ctor
        ~Model();//actual dtor
        
        //This class will be interfaced to other non-C# code
        //The plan is to use static methods on addresses in this space
        PORT static const char * makeModel(Model*& p_this);//allocator
        PORT static const char * destroyModel(Model* p_this);//deallocator
        PORT static const char * destroyAll();//risk of memory leaks may justify a kill switch
        //Allow user to get keys of the internal map
        PORT static const char * getNumSettings(const Model* p_this
        , size_t& p_numSettings);
        PORT static const char * getName(const Model* p_this
        , const size_t p_settingInd
        , size_t& p_numVals, const char *& p_name);
        //allow user to set keys (err if not existant or too small)
        PORT static const char * set(Model* p_this
        , const char * p_setting, const size_t p_ind, const double p_val);
        //allow user to set keys (add if not existant; grow if needed)
        PORT static const char * add(Model* p_this
        , const char * p_setting, const size_t p_ind, const double p_val);
        //allow user to get value
        PORT static const char * get(const Model* p_this
        , const char * p_setting, size_t p_ind
        , double& p_val);
        //basic file operations
        PORT static const char * load(Model* p_this
        , const char * p_filename);
        PORT static const char * save(const Model* p_this
        , const char * p_filename);
        //helper viewer method
        PORT static const char * toString(const Model* p_this,std::string& text);
        //basic modeling Operations 
        //Input size I to be defined in "InputSize" setting 0th element
        //Ouptput size O to be defined in "OutputSize" setting 0th element
        PORT static const char * train(Model* p_this
        , const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT);
        PORT static const char * test(const Model* p_this
        , const size_t p_T, const real* p_data_IxT
        , real* p_estimate_OxT);
        //basic test method
        PORT static const char * unitTests(int test);
        static size_t s_buffLen;
    protected:
        static Logging<Model> s_logger;//helper for error messages todo: consider using a static on Logging
    private:
        //internally stick to classes that will auto deconstruct whereever possible
        std::map<std::string,std::vector<double>> m_settings;
        std::map<std::string,std::vector<double>> m_parameters;
        //going to dump error mesages & string names here
        static char s_paramName[Logging<Model>::s_buffLen];

        //basic modeling Operations 
        //Input size I to be defined in "InputSize" setting 0th element
        //Ouptput size O to be defined in "OutputSize" setting 0th element
        virtual const char * train(const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT);
        virtual const char * test(const size_t p_T, const real* p_data_IxT, real* p_estimate_OxT) const;
};