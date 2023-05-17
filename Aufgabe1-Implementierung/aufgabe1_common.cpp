#include <bits/stdc++.h>

#ifndef AUFGABE1_COMMON
#define AUFGABE1_COMMON
namespace common{
    const int LOWER = 8;
    const int UPPER = 18;
    const int TLEN = 1000;
    
    struct ZoneRequest
    {
        int tStart;
        int tEnd;
        int zLen;
        int area;
        int localID;

        ZoneRequest(int tStart, int tEnd, int zLen, int localID = -1){
            this->tStart = tStart;
            this->tEnd = tEnd;
            this->zLen = zLen;
            this->area = (tEnd-tStart)*zLen;
            this->localID = localID;
        }
        ZoneRequest() = default;
    };
    
    struct PlacedRequest : ZoneRequest
    {
        int zStart;
        int zEnd;

        PlacedRequest(ZoneRequest &zRequest, int zStart) 
        : ZoneRequest(zRequest.tStart, zRequest.tEnd, zRequest.zLen, zRequest.localID){
            this->zStart = zStart;
            this->zEnd = zStart+ this->zLen;
        }
        PlacedRequest() = default;

        friend bool operator<(const PlacedRequest &a, const PlacedRequest &b){
            return std::tie(a.tStart, a.tEnd, a.localID, a.zStart, a.zEnd)<std::tie(b.tStart, b.tEnd, b.localID, b.zStart, b.zEnd);
        }
        friend bool operator==(const PlacedRequest &a, const PlacedRequest &b){
            return (a.tStart == b.tStart && a.tEnd == b.tEnd && a.zStart == b.zStart && a.zEnd == b.zEnd);
        }
    };
    
    struct ProposedChange
    {
        std::vector<PlacedRequest> colliders;
        PlacedRequest nPlaced;
        int addedArea;
        ProposedChange(std::vector<PlacedRequest> colliders, PlacedRequest nPlaced, int colliderArea){
            this->colliders = colliders;
            this->nPlaced = nPlaced;
            this->addedArea = nPlaced.area - colliderArea;
        }
        ProposedChange() = default;
    };
    
    struct TaskInput
    {
        std::vector<ZoneRequest> requests = {};
        #pragma region Optional Params
        int maxCycles = -1;
        //Structures
        bool forceSet = false;
        bool forceArray = false;
        //Randomization
        bool useRandomization = false;
        int maxRepetitions = -1;
        float maxRuntime = 0;
        int seed = -1;
        float considerElementProb = 0.5; 
        #pragma endregion
    };
    
    struct TaskOutput
    {
        std::set<PlacedRequest> placedRequests;
        int tArea;
        float runtime;
        TaskOutput(std::set<PlacedRequest> placedRequests){
            this->placedRequests = placedRequests;
            this->tArea = 0;
            for (PlacedRequest pReq : placedRequests){
                this->tArea += pReq.area;
            }
            this->runtime = 0;
        }
    };
    
    TaskInput readInput(std::string fileName){
        TaskInput tInput;
        std::ifstream fIn(fileName);
        int N;
        fIn >> N;
        int tStart, tEnd, zLen;
        for (int i = 0; i < N; i++)
        {
            fIn >> tStart >> tEnd >> zLen;
            tInput.requests.push_back(ZoneRequest(tStart, tEnd, zLen));
        }
        fIn.close();
        return tInput;
    } 

    void writeOutput(std::string fileName, TaskOutput &tOutput, bool verbose = false){
        auto vOnly = [verbose](std::string s){return (verbose ? s : "");};
        std::ofstream fOut(fileName);
        fOut << std::setprecision(9);
        fOut << vOnly("Laufzeit: ") << tOutput.runtime << vOnly("s") << '\n';
        fOut << vOnly("Einnahmen: ") << tOutput.tArea << vOnly("€")<<"\n";
        fOut << vOnly("Standplätze: ") << tOutput.placedRequests.size() << "\n";
        for (PlacedRequest pReq : tOutput.placedRequests){
            fOut << pReq.tStart <<" "<< pReq.tEnd <<" "<< pReq.zStart <<" "<<pReq.zEnd<<"\n";
        }
        fOut.close();
    }
    
    bool doCollide(PlacedRequest a, PlacedRequest b){
        if ((b.zStart <= a.zStart && a.zStart < b.zEnd) 
        || (b.zEnd >= a.zEnd && a.zEnd > b.zStart) 
        || (a.zStart <= b.zStart && b.zStart < a.zEnd)
        || (a.zEnd >= b.zEnd && b.zEnd > a.zStart)){
            if ((b.tStart <= a.tStart && a.tStart < b.tEnd) 
            || (b.tEnd >= a.tEnd && a.tEnd > b.tStart)
            || (a.tStart <= b.tStart && b.tStart < a.tEnd)
            || (a.tEnd >= b.tEnd && b.tEnd > a.tStart)){
                return true;
            }
        }
        return false;
    }

    bool checkNoCollisions(std::set<PlacedRequest> &placedRequests){
        std::vector<std::vector<int>> arr(UPPER-LOWER, std::vector<int>(TLEN, 0));
        for (PlacedRequest pReq : placedRequests){
            for (int col = pReq.tStart-LOWER; col < pReq.tEnd-LOWER; col++)
            {
                for (int row = pReq.zStart; row < pReq.zEnd; row++)
                {
                    arr[col][row] += 1;
                }
            }
        }
        for (int col = 0; col < UPPER-LOWER; col++)
        {
            for (int row = 0; row < TLEN; row++)
            {
                if (arr[col][row] > 1){
                    return false;
                }
            }
        }
        return true;
    }

    bool areaComp(const ZoneRequest &a, const ZoneRequest &b){
        return a.area < b.area;
    }

    bool changeComp(ProposedChange &a, ProposedChange &b){
        return a.addedArea < b.addedArea;
    }
}
#endif
