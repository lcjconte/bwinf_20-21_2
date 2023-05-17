#include <bits/stdc++.h>
#include <random>
#include <chrono>

#include <aufgabe1_common.cpp>

using namespace common;
using std::vector;
using std::pair;
using std::reference_wrapper;
using std::make_pair;
using std::set;
using std::chrono::high_resolution_clock;
using std::chrono::duration_cast;
using std::chrono::milliseconds;

namespace processing{
    struct Context
    {
        PlacedRequest nullRequest;
        set<PlacedRequest> placedRequests;
        vector<vector<PlacedRequest>> zArray; 
        TaskInput &tInput;
        vector<bool> isPlaced;
        bool didChange;
        Context(TaskInput &tInput) : tInput(tInput){
            this->placedRequests = {};
            ZoneRequest nullZone(0, 1, 1, -2);
            this->nullRequest = PlacedRequest(nullZone, 0);
            if (!tInput.forceSet){
                this->zArray = vector<vector<PlacedRequest>>(UPPER-LOWER, vector<PlacedRequest>(TLEN, this->nullRequest)); 
            }
        }
    };
    
    bool yesorno(float yesProb, std::default_random_engine &rnd){
        return (rnd() % 100) < (yesProb*100);
    }
    
    pair<vector<PlacedRequest>, int> findInSet(PlacedRequest &nPlaced, Context &ctx){
        int tArea = 0;
        vector<PlacedRequest> colliders;
        std::set<PlacedRequest>::iterator it;
        for (PlacedRequest pReq : ctx.placedRequests){
            if (doCollide(nPlaced, pReq)){
                tArea += pReq.area;
                colliders.push_back(pReq);
            }
        }
        return make_pair(colliders, tArea);
    }
    
    pair<vector<PlacedRequest>, int> findInArray(PlacedRequest &nPlaced, Context &ctx){
        int tArea = 0;
        set<PlacedRequest> colliders;
        for (int col = nPlaced.tStart-LOWER; col < nPlaced.tEnd-LOWER; col++)
        {
            for (int row = nPlaced.zStart; row < nPlaced.zEnd; row++)
            {
                PlacedRequest pReq = ctx.zArray[col][row];
                if (pReq.localID != -2 && colliders.find(pReq) == colliders.end()){
                    colliders.emplace(pReq);
                    tArea += pReq.area;
                }
            }
            
        }
        return make_pair(vector<PlacedRequest>(colliders.begin(), colliders.end()), tArea);
    }
    
    pair<vector<PlacedRequest>, int> findColliders(PlacedRequest nPlaced, Context &ctx){
        if (ctx.tInput.forceSet){
            return findInSet(nPlaced, ctx);
        }
        else if (ctx.tInput.forceArray){
            return findInArray(nPlaced, ctx);
        }
        else if (ctx.placedRequests.size() < nPlaced.area){
            return findInSet(nPlaced, ctx);
        }
        else{
            return findInArray(nPlaced, ctx);
        }
    }
    
    void applyChange(ProposedChange change, Context &ctx){
        for (PlacedRequest collider : change.colliders){
            if (!ctx.tInput.forceSet){
                for (int col = collider.tStart-LOWER; col < collider.tEnd-LOWER; col++)
                {
                    for (int row = collider.zStart; row < collider.zEnd; row++)
                    {
                        ctx.zArray[col][row] = ctx.nullRequest;
                    }
                }
                
            }
            ctx.placedRequests.erase(collider);
            ctx.isPlaced[collider.localID] = false;
        }
        PlacedRequest nPlaced = change.nPlaced;
        if (!ctx.tInput.forceSet){
            for (int col = nPlaced.tStart-LOWER; col < nPlaced.tEnd-LOWER; col++)
            {
                for (int row = nPlaced.zStart; row < nPlaced.zEnd; row++)
                {
                    ctx.zArray[col][row] = nPlaced;
                }
            }
        }
        ctx.placedRequests.emplace(nPlaced);
        ctx.isPlaced[nPlaced.localID] = true;
        ctx.didChange = true;
    }

    TaskOutput process_standard(TaskInput tInput){
        auto sTime = high_resolution_clock::now();

        std::default_random_engine rnd;
        if (tInput.useRandomization){
            if (tInput.seed == -1){
                rnd.seed(time(nullptr));
            }
            else{
                rnd.seed(tInput.seed);
            }
        }

        vector<ZoneRequest> requests = tInput.requests;
        std::stable_sort(requests.begin(), requests.end(), areaComp);

        Context ctx(tInput);
        ctx.isPlaced = vector<bool>(requests.size(), false);

        for (int i = 0; i < requests.size(); i++)
        {
            requests[i].localID = i;
        }
        ctx.didChange = true;
        bool finalRound = false;
        int cycleCount = 0;
        while ((ctx.didChange || finalRound) && (tInput.maxCycles == -1 || cycleCount < tInput.maxCycles))
        {
            cycleCount += 1;
            ctx.didChange = false;

            for (ZoneRequest req : requests){
                if (ctx.isPlaced[req.localID]){
                    continue;
                }
                if (tInput.useRandomization){
                    if (!finalRound && !yesorno(tInput.considerElementProb, rnd)){
                        continue;
                    }
                }
                vector<ProposedChange> pChanges;
                for (int zStart = 0; zStart < TLEN-req.zLen; zStart++)
                {
                    PlacedRequest nPlaced(req, zStart);
                    vector<PlacedRequest> colliders;
                    int tArea;
                    pair<vector<PlacedRequest>, int> res = findColliders(nPlaced, ctx);
                    colliders = res.first;
                    tArea = res.second;
                    if (tArea < req.area){
                        pChanges.push_back(ProposedChange(colliders, nPlaced, tArea));
                    }
                }
                if (pChanges.size() == 0){
                    continue;
                }
                else{
                    ProposedChange chosenChange = *(std::max_element(pChanges.begin(), pChanges.end(), changeComp));
                    applyChange(chosenChange, ctx);
                }
            }

            if (tInput.useRandomization){
                if (!ctx.didChange && !finalRound){
                    finalRound = true;
                }
                else{
                    finalRound = false;
                }
            }
        }
        TaskOutput tOutput(ctx.placedRequests);
        auto eTime = high_resolution_clock::now();
        auto d = duration_cast<milliseconds>(eTime-sTime);
        tOutput.runtime = d.count()/1000.0;
        return tOutput;
    }
    
}

int main(){
    for (int i = 1; i < 8; i++)
    {
        std::string fName = "flohmarkt"+std::string(1, '0'+i)+".txt";
        TaskInput tInput = readInput(fName);
        std::cout << "Processing: " << fName << std::endl;
        TaskOutput tOutput = processing::process_standard(tInput);
        writeOutput("ausgabe"+std::string(1, '0'+i)+".txt", tOutput, true);
        std::cout << tOutput.runtime << std::endl;
        std::cout << tOutput.tArea << std::endl;
        std::cout << checkNoCollisions(tOutput.placedRequests) << std::endl;
    }
    
    return 0;
}
