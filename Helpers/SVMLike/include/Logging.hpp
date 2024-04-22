#pragma once
#include <string>
#include <vector>

template <class T> class Logging{
    public:
        //todo:put file based logging here; for now just add messageing for const char *
        //max buffer length used by Model
        static const size_t s_buffLen=1024;
        Logging(){ 
            //todo:consider a file to dump to
        }
        ~Logging(){ 
            //hopefully nothing
        }
        const char * setStatus(const std::string& msg,const std::string& loc){
            std::string fullMsg=msg+" in "+loc;
            size_t chars=fullMsg.size()<s_buffLen-1?fullMsg.size():s_buffLen-1;//always keep a null at the end
            std::copy(&fullMsg[0],&fullMsg[0]+chars,s_status);
            s_status[chars]='\0';
            return &s_status[0];
        }
        const char * addTrackedObject(T* obj){
            s_trackedObjects.push_back(obj);
            return NULL;//todo:consider returning size of non-null entries
        }
        const char * removeTrackedObject(T* obj, bool deleteAlso){
            size_t cleared=0;
            for(size_t ind=0;ind<s_trackedObjects.size();ind++){
                if(s_trackedObjects[ind]==obj)
                    s_trackedObjects[ind]=NULL;
                if(s_trackedObjects[ind]==NULL)
                    cleared++;
            }
            if(deleteAlso)
                delete obj;
            if(cleared==s_trackedObjects.size())
                s_trackedObjects.clear();
            return NULL;
        }
        const char * deleteAllTrackedObjects(){
            for(size_t ind=0;ind<s_trackedObjects.size();ind++)
                if(s_trackedObjects[ind]!=NULL)
                    delete s_trackedObjects[ind];
            s_trackedObjects.clear();
            //todo add some summary information to this output
            return NULL;
        }
        size_t  numAllocated(){
        return s_trackedObjects.size();
    }

    private:
        //going to dump error mesages & std::string names here
        char s_status[s_buffLen];
        std::vector<T*> s_trackedObjects;

};
//implementation in header...
//https://stackoverflow.com/questions/495021/why-can-templates-only-be-implemented-in-the-header-file
