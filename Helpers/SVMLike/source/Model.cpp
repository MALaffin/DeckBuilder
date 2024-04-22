#include "Model.hpp"
#include "Logging.hpp"
using namespace std;
#include <stdio.h>

//#define extraDebug
#if defined extraDebug
#include <iostream>
#endif

//statics
Logging<Model> Model::s_logger=Logging<Model>();
size_t Model::s_buffLen=Logging<Model>::s_buffLen;
char Model::s_paramName[Logging<Model>::s_buffLen];

Model::Model(){
    //initialize common settings to invalid state
    m_settings["InputSize"].push_back(-1);
    m_settings["OutputSize"].push_back(-1);
    m_parameters["ModelType"].push_back(-1);
    s_logger.setStatus("OK",__FUNCTION__);
}

Model::~Model(){
    //hopefully no work    
}

const char * Model::makeModel(Model*& p_this){
    p_this = new Model();
    return s_logger.addTrackedObject(p_this);
}

const char * Model::destroyModel(Model* p_this){
    return s_logger.removeTrackedObject(p_this,true);
}

const char * Model::destroyAll(){
    return s_logger.deleteAllTrackedObjects();
}

const char * Model::getNumSettings(const Model* p_this
, size_t& p_numSettings){
    p_numSettings=p_this->m_settings.size();
    return NULL;
}

const char * Model::getName(const Model* p_this
, const size_t p_settingInd, size_t& p_numVals, const char *& p_name){
    if(p_settingInd>p_this->m_settings.size())
        return s_logger.setStatus("index too big",__FUNCTION__);
    NamedValues::const_iterator it=p_this->m_settings.begin();
    advance(it,p_settingInd);
    size_t chars=it->first.size()<s_buffLen-1?it->first.size():s_buffLen-1;//always keep a null at the end
    copy(&it->first[0],&it->first[0]+chars,s_paramName);
    s_paramName[chars]='\0';
    p_name=s_paramName;
    p_numVals=it->second.size();
    return NULL;
}

const char * Model::set(Model* p_this, const char * p_setting, const size_t p_ind, const double p_val){
    NamedValues::iterator it=p_this->m_settings.find(string(p_setting));
    if(it==p_this->m_settings.end())
        return s_logger.setStatus("'"+string(p_setting) +"' not found",__FUNCTION__);
    if(it->second.size()<p_ind+1)
        return s_logger.setStatus("'"+string(p_setting) +"' too small",__FUNCTION__);
    it->second[p_ind]=p_val;
    return NULL;
}

const char * Model::add(Model* p_this, const char * p_setting, const size_t p_ind, const double p_val){
    NamedValues::iterator it=p_this->m_settings.find(string(p_setting));
    if(it==p_this->m_settings.end()){
        p_this->m_settings[string(p_setting)];
        it=p_this->m_settings.find(string(p_setting));
    }
    if(it->second.size()<p_ind+1){
        it->second.resize(p_ind+1);
    }
    it->second[p_ind]=p_val;
    return NULL;
}

const char * Model::get(const Model* p_this, const char * p_setting, size_t p_ind, double& p_val){
    NamedValues::const_iterator it=p_this->m_settings.find(p_setting);
    if(it==p_this->m_settings.end())
        return s_logger.setStatus("'"+string(p_setting) +"' not found",__FUNCTION__);
    if(it->second.size()<p_ind+1)
        return s_logger.setStatus("'"+string(p_setting) +"' does not have enough elements",__FUNCTION__);
    p_val=it->second[p_ind];
    return NULL;
}

const char * saveMap(FILE* loc, const map<string,vector<double>>& p_info){
    size_t s=p_info.size();
    fwrite(&s,sizeof(size_t),1,loc);
    for(NamedValues::const_iterator it=p_info.begin();
    it!=p_info.end();++it){
        string str=it->first;
        s=str.size();
        fwrite(&s,sizeof(size_t),1,loc);
        fwrite(&str[0],sizeof(char),str.size(),loc);
        s=it->second.size();
        fwrite(&s,sizeof(size_t),1,loc);
        for(size_t ind=0;ind<s;ind++){
            fwrite(&it->second[ind],sizeof(double),1,loc);
            #if defined extraDebug
            std::cout<<"wrote "<<str<<","<<ind<<","<<it->second[ind]<<"\r\n";
            #endif
        }
    }
    return NULL;
}    
const char * Model::save(const Model* p_this, const char * p_filename){
    FILE * loc=fopen( p_filename , "w");
    if(!loc)
        return s_logger.setStatus("'"+string(p_filename) +"' failed to open for write",__FUNCTION__);
    const char * err = saveMap(loc,p_this->m_settings);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' failed ot save settings",__FUNCTION__);
    err = saveMap(loc,p_this->m_parameters);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' failed ot save parameters",__FUNCTION__);
    fclose(loc);
    return NULL;
}
const char * readMap(FILE* loc, map<string,vector<double>>& p_info){
    size_t sizeInfo;
    fread(&sizeInfo,sizeof(size_t),1,loc);
    for(size_t param=0;param<sizeInfo;param++){
        size_t s;
        fread(&s,sizeof(size_t),1,loc);
        char str[Model::s_buffLen];
        fread(&str,sizeof(char),s,loc);
        str[s]='\0';
        string key=string(str);
        p_info[key];
        fread(&s,sizeof(size_t),1,loc);
        p_info[key].resize(s);
        for(size_t ind=0;ind<s;ind++){
            double val;
            fread(&val,sizeof(double),1,loc);
            p_info[key][ind]=val;

            #if defined extraDebug
            std::cout<<"loaded "<<key<<","<<ind<<","<<val<<"\r\n";
            #endif
        }
    }
    return NULL;
}    
const char * Model::load(Model* p_this, const char * p_filename){
    FILE * loc=fopen( p_filename , "r");
    if(!loc)
        return s_logger.setStatus("'"+string(p_filename) +"' failed to open for read",__FUNCTION__);
    const char * err = readMap(loc,p_this->m_settings);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' failed to load settings",__FUNCTION__);
    err = readMap(loc,p_this->m_parameters);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' failed to load parameters",__FUNCTION__);
    fclose(loc);
    return NULL;
}

const char * Model::train(Model* p_this
, const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT){
    return p_this->train(p_T, p_data_IxT, p_trueth_OxT);
}
const char * Model::test(const Model* p_this
, const size_t p_T, const real* p_data_IxT, real* p_estimate_OxT){
    return p_this->test(p_T, p_data_IxT, p_estimate_OxT);
}

const char * Model::train(const size_t p_T, const real* p_data_IxT, const real* p_trueth_OxT){
    return "virtual train not implemented";
}
const char * Model::test(const size_t p_T, const real* p_data_IxT, real* p_estimate_OxT) const{
    return "virtual test not implemented";
}

const char * Model::toString(const Model* p_this, string& text){
    const char * err;
    size_t numSettings;
    err=getNumSettings(p_this, numSettings);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' could not get numSettings",__FUNCTION__);
    for(size_t s=0;s<numSettings;s++){
        size_t numVals1;
        const char * name1;
        err=getName(p_this,s,numVals1,name1);
        if(err)
            return s_logger.setStatus("'"+string(err) +"' could not getName",__FUNCTION__);
        string key = name1;
        text=text+key;
        for(size_t ind=0;ind<numVals1;ind++){
            double val;
            err=get(p_this,name1,ind,val);
            if(err)
                return s_logger.setStatus("'"+string(err) +"' could not get val",__FUNCTION__);            
            text=text+" "+ to_string(val);
            #if defined extraDebug
            std::cout<<key<<"["<<ind<<"]="<<val<<"\r\n";
            #endif
        }
        text=text+"\r\n";
    }
    return NULL;
}

const char * Model::unitTests(int test){
    (void)test;//todo add test controls with int test
    const char * err;
    
    Model* test1;
    err=makeModel(test1);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' test1 create",__FUNCTION__);
    if(s_logger.numAllocated()!=1)
        return s_logger.setStatus("'"+string(err) +"' s_trackedObjects check 1 ",__FUNCTION__);

    #if defined extraDebug
    std::cout<<"set1\r\n";
    #endif

    err=Model::set(test1, "InputSize", 0, 1);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' set input size",__FUNCTION__);
    err=Model::set(test1, "OutputSize", 0, 2);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' set output size",__FUNCTION__);
    #if defined extraDebug
    std::cout<<"add1\r\n";
    #endif
    err=Model::add(test1, "NewSetting", 1, 3);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' set new 0",__FUNCTION__);
    err=Model::set(test1, "NewSetting", 0, 4);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' set new 1",__FUNCTION__);
    
    #if defined extraDebug
    std::cout<<"save1\r\n";
    #endif
    err=Model::save(test1, "unitTestSaveModel.mdl");
    if(err)
        return s_logger.setStatus("'"+string(err) +"' save",__FUNCTION__);

    Model* test2;
    err=makeModel(test2);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' test2 create",__FUNCTION__);
    if(s_logger.numAllocated()!=2)
        return s_logger.setStatus("'"+string(err) +"' s_trackedObjects check 2 ",__FUNCTION__);
    
    #if defined extraDebug
    std::cout<<"load1\r\n";
    #endif
    err=Model::load(test2, "unitTestSaveModel.mdl");
    if(err)
        return s_logger.setStatus("'"+string(err) +"' save",__FUNCTION__);
    
    #if defined extraDebug
    std::cout<<"compare1\r\n";
    #endif
    string s1,s2;
    err=toString(test1,s1);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' tostring1",__FUNCTION__);
    err=toString(test2,s2);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' tostring2",__FUNCTION__);
    if(s1!=s2)
        return s_logger.setStatus("'"+string(err) +"' compare failed",__FUNCTION__);

    #if defined extraDebug
    std::cout<<"destroy1\r\n";
    #endif
    err=destroyModel(test1);
    if(err)
        return s_logger.setStatus("'"+string(err) +"' test1 destroy",__FUNCTION__);
    if(s_logger.numAllocated()!=2)
        return s_logger.setStatus("s_trackedObjects check 3 ",__FUNCTION__);


    #if defined extraDebug
    std::cout<<"destroy2\r\n";
    #endif
    err=destroyAll();
    if(err)
        return s_logger.setStatus("'"+string(err) +"' destroy all",__FUNCTION__);
    if(s_logger.numAllocated()!=0)
        return s_logger.setStatus("s_trackedObjects check 4 ",__FUNCTION__);

    #if defined extraDebug
    std::cout<<"all ok\r\n";
    #endif
    return NULL;
}
