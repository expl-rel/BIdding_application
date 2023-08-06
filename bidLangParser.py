#!/usr/bin/env python3
# -- coding: utf-8 --
"""
Created on Tue Mar  1 09:58:32 2022

@author: nagaaneeshmylavarapu
"""
import sys
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
from py2neo import *


class SuitCards:
    def __init__(self):
        self.suitHcp=[0,10]
        self.suitLength=[0,13]
        
        #Cards of suit in order A,K,Q,T,9,...,2
        # 0:Maybe, 1:Yes, -1:No
        self.cards=[0]*13
        
    def eq(self, other): 
        
        if not isinstance(other, SuitCards):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.suitHcp == other.suitHcp and 
        self.suitLength == other.suitLength and self.cards==other.cards)


class PlayerHand:
    def __init__(self):
        self.hcpBounds=[0,37]
        self.totalPoints=[0,40]
        #Cards of holder in order of suits S,H,D,C
        self.suits=[SuitCards(),SuitCards(),SuitCards(),SuitCards()]

        self.longestSuit=None
        
    def eq(self, other):
        
        if not isinstance(other, PlayerHand):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.hcpBounds == other.hcpBounds and 
        self.totalPoints==other.totalPoints and self.suits == other.suits and 
        self.longestSuit==other.longestSuit)



class BidDescription:
    def __init__(self):
        #Description of bid
        #Like pre emptive or support or cue
        self.description="Custom"
        
        #If bid is supporting then Number of cards of support
        self.numCards=None
        
        #Suit type that is supported
        self.suit=None
        
        #Any additional Information
        self.info=None

class BidCategory:
    def __init__(self):
        #Type of bid
        #Like opening, response, overcall, asking, respondingToAsk
        self.categoryOfBid="Custom"
        
        #If categoryOfBid is respondingToAsk then 
        #reference to askingBid node as key string
        #Any additional description
        self.info=None

class BidImpact:
    def __init__(self):
        self.bidImpactCategory="NonForcing"
        self.info=None

class BidNode:
    def __init__(self, isConvention=False):
        #Forcing, non forcing, invitational, sign off
        self.bidImpact=BidImpact()
        
        #bidding convention this node is part of
        self.isConvention=isConvention
        
        self.longestSuit=None
        self.bidSystem=None
        self.bid=None
        self.forcing=False
        self.isParentForcing=False
        self.allowedBids=[True]*38
        #self.opening=False
        self.hand=PlayerHand()
       
        #Like opening, response, overcall, asking, respondingToAsk
        self.biddingCategory=BidCategory()
        
        #Like pre emptive or support or cue
        self.biddingDescription=BidDescription()

class DAGFunctions:
    def __init__(self,graphName):
        self.graph=graphName
        self.bidToInt={"1C":0,"1D":1,"1H":2,"1S":3,"1NT":4,
                        "2C":5,"2D":6,"2H":7,"2S":8,"2NT":9,
                        "3C":10,"3D":11,"3H":12,"3S":13,"3NT":14,
                        "4C":15,"4D":16,"4H":17,"4S":18,"4NT":19,
                        "5C":20,"5D":21,"5H":22,"5S":23,"5NT":24,
                        "6C":25,"6D":26,"6H":27,"6S":28,"6NT":29,
                        "7C":30,"7D":31,"7H":32,"7S":33,"7NT":34,
                        "P":35,"Dbl":36,"ReDbl":37}

    def createNode(self,curNode):
        errorString=None
        if not isinstance(curNode, BidNode):
            errorString="Given parameter is not of type BidNode"
            print(errorString)
            return [None,errorString]
        ptrNode=Node()
        self.graph.create(ptrNode)
        labelName=""
        if curNode.isConvention==True:
            labelName+="C_"
        else:
            labelName+="B_"
        labelName+=curNode.bidSystem
        ptrNode.add_label(labelName)
        ptrNode['bidSystem']=curNode.bidSystem
        ptrNode['bid']=curNode.bid
        ptrNode['longestSuit']=curNode.longestSuit
        ptrNode['isConvention']=curNode.isConvention
        ptrNode['SuitLengthLb']=[curNode.hand.suits[0].suitLength[0],
                                 curNode.hand.suits[1].suitLength[0],
                                 curNode.hand.suits[2].suitLength[0],
                                 curNode.hand.suits[3].suitLength[0]]
        
        ptrNode['SuitLengthUb']=[curNode.hand.suits[0].suitLength[1],
                                 curNode.hand.suits[1].suitLength[1],
                                 curNode.hand.suits[2].suitLength[1],
                                 curNode.hand.suits[3].suitLength[1]]
        
        ptrNode['SuitHcpLb']=[curNode.hand.suits[0].suitHcp[0],
                              curNode.hand.suits[1].suitHcp[0],
                              curNode.hand.suits[2].suitHcp[0],
                              curNode.hand.suits[3].suitHcp[0]]
        
        ptrNode['SuitHcpUb']=[curNode.hand.suits[0].suitHcp[1],
                              curNode.hand.suits[1].suitHcp[1],
                              curNode.hand.suits[2].suitHcp[1],
                              curNode.hand.suits[3].suitHcp[1]]
        
        ptrNode['HcpLb']=curNode.hand.hcpBounds[0]
        ptrNode['HcpUb']=curNode.hand.hcpBounds[1]
        tmpList=[]
        for j in range(4):
            tmpList+=curNode.hand.suits[j].cards
        ptrNode['SuitCards']=tmpList
        ptrNode['TotalPointsLb']=curNode.hand.totalPoints[0]
        ptrNode['TotalPointsUb']=curNode.hand.totalPoints[1]
        ptrNode['Forcing']=curNode.forcing
        ptrNode['AllowedBids']=curNode.allowedBids
        ptrNode['bidImpact']=curNode.bidImpact.bidImpactCategory
        ptrNode['bidImpactInfo']=curNode.bidImpact.info
        ptrNode['bidCategory']=curNode.biddingCategory.categoryOfBid
        ptrNode['bidCategoryInfo']=curNode.biddingCategory.info
        ptrNode['bidDescription']=curNode.biddingDescription.description
        ptrNode['bidDescriptionInfo']=curNode.biddingDescription.info
        ptrNode['supportOrCueSuit']=curNode.biddingDescription.suit
        ptrNode['supportCount']=curNode.biddingDescription.numCards
        
        ptrNode['isRoot']=False
        ptrNode['highestIncomingBid']=-1
        ptrNode['nodeId']=ptrNode.identity
        # print(type(ptrNode))
        return ptrNode

    def createRoot(self,bidSystemName,fl):
        #Create a bidNode with default values
        tmpNode=BidNode()
        tmpNode.bidSystem=bidSystemName
        rootNode=self.createNode(tmpNode)
        rootNode['isRoot']=True
        labelName=""
        if fl==3:
            rootNode['isConvention']=True
            labelName+="C_"
        else:
            rootNode['isConvention']=False
            labelName+="B_"
        labelName+=bidSystemName
        rootNode.add_label(labelName)
        rootNode['bidSystem']=bidSystemName
        rootNode['highestIncomingBid']=-1
        #rootNode['nodeId']=rootNode.identity
        self.graph.push(rootNode)
        return rootNode

    def createBiddingSystem(self,bidSystemName,fl):
    #     Check if a node with attribute as bidSystemName exists 
    #if no then create graph else return -1 that it already exists
        query="""match (n{bidSystem:$val})
                 return count(n)"""
        co=self.graph.evaluate(query,val=bidSystemName)
        if (co!=0):
            print("Bidding system already exists")
            return None
        else:
            rootNode=self.createRoot(bidSystemName,fl)
            return rootNode



    def findRoot(self,bidSystemName):
        query="""match (n{bidSystem:$val,isRoot:True})
                 return n"""
        rootNode=self.graph.evaluate(query,val=bidSystemName)
        return rootNode


    def findNode(self,bidSystemName,key):
        rootNode=self.findRoot(bidSystemName)
        if rootNode==None:
            return None
        if key=="":
            return rootNode
        l1=key.split('-')
        #print(l1)
        #We have a list of edges from the root 
        #that we need to traverse and find the end node.
        #for writing the query we need to create a string
        queryString="match (n) where ({nodeId:"+str(rootNode.identity)+"})"
        for bval in range(len(l1)-1):
            queryString+="-[{BidValue:'"+l1[bval]+"'}]->()"
        queryString+="-[{BidValue:'"+l1[len(l1)-1]+"'}]"
        queryString+="->(n) return n"
        foundNode=self.graph.evaluate(queryString)
        return foundNode


    def insertChild(self,bidSystemName,bidNode,parentNode,bidValue):
        #Check if parent node exists 
        #if no then return None
        #Else check if an outgoing edge with the same bid exists
        #If no return new child node inserted else return None
        if parentNode==None:
            return None
        edgeLabel="BidSystem_"+bidSystemName
        # q0="""match (x{nodeId:$val1,bidSystem:$val2})-[{BidValue:$val3,"""+edgeLabel+""":true}]->(n1)
        #     return count(n1)"""
        
        # co1=self.graph.evaluate(q0,val1=parentNode.identity,val2=bidSystemName,val3=bidValue)
        # if co1!=0:
        #   print("A node with this bidvalue as child already exists")
        #   return None
        cbid=self.bidToInt[bidValue]
        if parentNode['AllowedBids'][cbid]==False:
            print("A node with this bidvalue as child already exists")
            return None
        else:
            parentNode['AllowedBids'][cbid]=False
            childNode=self.createNode(bidNode)
            #childNode['isRoot']=False
            # print(type(childNode))
            childNode['bidSystem']=bidSystemName
            childNode['bid']=bidValue

            #childNode['nodeId']=childNode.identity
            if bidValue=="P":
                childNode['highestIncomingBid']=parentNode['highestIncomingBid']
            else:
                childNode['highestIncomingBid']=self.bidToInt[bidValue]
            #For the child node all bids less than or equal to highest incoming bid become false
            for cbid in range(0,childNode['highestIncomingBid']+1):
                childNode['AllowedBids'][cbid]=False
            edgeLabel="BidSystem_"+bidSystemName    
            self.graph.push(childNode)
            self.graph.push(parentNode)
            bval="BidValue"
            el="edgeLabel"
            r=Relationship(parentNode,childNode)
            r['BidValue']=bidValue
            r[edgeLabel]=True
            self.graph.create(r)
            return childNode


    def addSubtree(self,bidSystemName,curNode,newChild):
        if curNode==None:
            print("Currrent Node is None")
            return False
        if newChild==None:
            print("New node is none")
            return False
        if curNode['highestIncomingBid']!=-1 and curNode['highestIncomingBid']>=newChild['highestIncomingBid']:
            print("The highest incoming bid at current node is greater than that of subtree to be added. Hence the subtree cannot be added")
            return False
        bidValue=newChild['bid']
        edgeLabel="BidSystem_"+bidSystemName
        bidsAllowed=curNode['AllowedBids']
        cbid=self.bidToInt[bidValue]
        if bidsAllowed[cbid]==False:
            print("A node with this bidvalue as child already exists")
            return False
        curNode['AllowedBids'][cbid]=False
        self.graph.push(curNode)  
        r=Relationship(curNode,newChild)
        r['BidValue']=bidValue
        r[edgeLabel]=True
        self.graph.create(r)
        return True



    def addConvention(self,bidSystemName,conventionName, parentNode, bidValueList):
        if parentNode==None:
            print("Parent node does not exist")
            return False
        # print(conventionName)
        conventionRootNode=self.findRoot(conventionName)
        print(conventionName)
        if conventionRootNode==None:
            print("Convention root node does not exist")
            return False
        edgeLabel="BidSystem_"+bidSystemName
        for bidValue in bidValueList:
            cbid=self.bidToInt[bidValue]
            if parentNode['AllowedBids'][cbid]==False:
                print("Parent node already has a bid as child from the bid Value list to be added")
                return False
            q0="""match (x{nodeId:$val1})-[{BidValue:$val3}]->(n1)
                  match (x1{nodeId:$val2})
                  create (x1)-[rel:"""+edgeLabel+"""{BidValue:$val3,"""+edgeLabel+""":true}]->(n1)
                  return n1"""
        
            co1=self.graph.evaluate(q0,val1=conventionRootNode.identity,val2=parentNode.identity,val3=bidValue)
            parentNode['AllowedBids'][cbid]=False
            self.graph.push(parentNode)
        return True

    def deleteAllNodes(self,bidSystemName):
        q0="""match (x{bidSystem:$val})
               detach delete x"""
        self.graph.evaluate(q0,val=bidSystemName)
    
class BidParser:

    def __init__(self,authName,authPwd):
        self.bidDict={}
        self.graphName=Graph("neo4j://localhost:7687", auth=(authName,authPwd))
        self.orderedBids=["1C","1D","1H","1S","1NT",
                         "2C","2D","2H","2S","2NT",
                         "3C","3D","3H","3S","3NT",
                         "4C","4D","4H","4S","4NT",
                         "5C","5D","5H","5S","5NT",
                         "6C","6D","6H","6S","6NT",
                         "7C","7D","7H","7S","7NT",
                         "P","dbl","redbl"]
        self.df=DAGFunctions(self.graphName)

    # To be replaced by http/bolt connection
    # def graphDBConnector(self,authName,authPwd):
        # self.graphName = Graph(auth=(authName.authPwd))

    # This function is used to delete all the nodes in the bidding system because of an inconsistency
    # The inconsistency can arise due to:
    #   1. An undefined convention
    #   2. A node redefining the meaning of an existing node.
    #       This can occur because a node can have a 
    
    def deleteAndExit(self,bidSystemName):
        self.df.deleteAllNodes(bidSystemName)
        exit()


     =============================================================================
    # key checker ensures that 
    # 1.bids proceed in increasing order 
    # 2.there can be no further bids after 3 passes.
    # 3.Add rules for dbl and redbl
    # =============================================================================
    def keyChecker(self,key):
        orderedBids=["1C","1D","1H","1S","1NT",
                     "2C","2D","2H","2S","2NT",
                     "3C","3D","3H","3S","3NT",
                     "4C","4D","4H","4S","4NT",
                     "5C","5D","5H","5S","5NT",
                     "6C","6D","6H","6S","6NT",
                     "7C","7D","7H","7S","7NT",
                     "P","dbl","redbl"]
        bidsList=key.split('-')
        prevInd=0
        cntP=0
        for i in range(len(bidsList)):
            val=bidsList[i]
            if val not in orderedBids:
                return False
            else:
                cind=orderedBids.index(val)
                if val=="P":
                    cntP+=1
                    if cntP==3:
                        if i < len(bidsList-1):
                            return False
                else:
                    cntP=0
                    if cind<=34:
                        if cind<=prevInd:
                            return False
                        prevInd=cind
        return True
                    

    def lineAndWordNumber(self,ind,totLen):
        prevLen=0
        for i in range(len(totLen)):
            if ind<totLen[i]+prevLen:
                return [i+1,ind-prevLen+1]
            prevLen+=totLen[i]
        return [-1,-1]


    def findElseCreateNode(self,bidVal,bidSystemName,isConvention=False):
        # l1=bidVal.split('-')
        foundNode=self.df.findNode(bidSystemName,bidVal)
        if foundNode!=None:
            return foundNode
        else:
            print(bidVal)
            l1=bidVal.split('-')
            print(l1)
            parentNode=None
            newNode=BidNode(isConvention)
            newNode.bidSystem=bidSystemName
            newNode.bid=l1[len(l1)-1]
            if len(l1)==1:
                parentNode=self.df.findRoot(bidSystemName)
            else:
                parBidVal='-'.join(l1[:len(l1)-1])
                parentNode=self.findElseCreateNode(parBidVal,bidSystemName)
            print("Problem: "+l1[len(l1)-1])
            print(l1)
            foundNode=self.df.insertChild(bidSystemName,newNode,parentNode,l1[len(l1)-1])
            if foundNode==None:
                print("Problem while creating parent node in findElseCreateNode function")
                self.deleteAndExit(bidSystemName)
            else:
                return foundNode

    def nodeCreator(self,bidVal, bidNode,bidSystemName,isConvention=False):
        l1=bidVal.split('-')
        print(bidVal)
        # print(parBidVal)
        parBidVal='-'.join(l1[:len(l1)-1])
        print(parBidVal)
        parentNode=self.findElseCreateNode(parBidVal,bidSystemName,isConvention)
        newNode=self.df.insertChild(bidSystemName,bidNode,parentNode,l1[len(l1)-1])
        if newNode==None:
            print("Problem in nodeCreator function")
            self.deleteAndExit(bidSystemName)

    def subtreeCreator(self,bidSystemName,curBidVal,baseBidVal,isConvention=False):
        l1=bidVal.split('-')
        parBidVal='-'.join(l1[:len(l1)-1])
        parentNode=self.findElseCreateNode(parBidVal,bidSystemName,isConvention)
        foundNode=self.df.findNode(baseBidVal,bidSystemName)
        if foundNode==None:
            print("Base bid val: "+baseBidVal+" not found while trying to add subtree")
            self.deleteAndExit(bidSystemName)

        self.df.addSubtree(bidSystemName,parentNode,foundNode)

    def conventionAdder(self,bidSystemName,conventionName,bidVal):
        l1=bidVal.split('-')
        parBidVal='-'.join(l1[:len(l1)-1])
        parentNode=self.findElseCreateNode(parBidVal,bidSystemName)
        bidValueList=l1[len(l1)-1].split(',')
        bVal=self.df.addConvention(bidSystemName,conventionName, parentNode, bidValueList)
        if bVal==False:
            print("Error while adding convention: "+conventionName)
            print("The given bid value is: "+bidVal)
            self.deleteAndExit(bidSystemName)

    def graphCreator(self,bidDict,bidSystemName,isConvention=False):
        # Need to replace this with a function to connect to server located remotely
        # graphName = Graph(auth=("neo4j", "aneesh"))
        # df=DAGFunctions(graphName)
        # Sort the dict based on length of keys
        bidDictList = sorted(list(bidDict.items()), key = lambda key : len(key[0].split('-')))
      
        # reordering to dictionary  
        finBidDict = {ele[0] : ele[1]  for ele in bidDictList}
        flval=1
        if isConvention==True:
            flval=3
        rootNode=self.df.createBiddingSystem(bidSystemName,flval)
        if rootNode==None:
            exit()

        for keyBid in finBidDict:
            if finBidDict[keyBid][1]==1:
                self.nodeCreator(keyBid,finBidDict[keyBid][0],bidSystemName,isConvention)
            elif finBidDict[keyBid][1]==2:
                self.subtreeCreator(bidSystemName,keyBid,finBidDict[keyBid][0],isConvention)
            elif finBidDict[keyBid][1]==3:
                self.conventionAdder(bidSystemName,finBidDict[keyBid][0],keyBid)


    def parseBidLang(self,filename,bidSystemName,isConvention=False):
        wl=[]
        totLen=[]
        with open(filename) as f:
            for line in f:
                cLen=len(line.split())
                if cLen>0:
                    totLen.append(cLen)
                    
                    for word in line.split():
                        wl.append(word)
            # wl=[word for line in f for word in line.split()]
        ind=0
        bidDict={}
        convBidDict={}
    # =============================================================================
    #     Any category can have an info inbetween the keywords -infoBegin and -infoEnd
    # =============================================================================
        bidCatList=["Opening","Asking","RespondingToAsk","Custom", "Response", "Overcall"]
        bidImpList=["NonForcing", "Forcing", "GameForcing", "Invitational", "GameInvitational", "SlamInvitational", "SignOff", "Custom"]
        bidDesList=["Preemptive", "Support", "Cue", "CueFirstRound", "CueSecondRound", "Custom"]
        suitList=["club","diamond","heart","spade"]
        keyValues=["-key","-convention","-conventionKey","-bidDescription","-bidCategory","-bidImpact","-infoBegin",
        "-infoEnd","-spadeSuitLengthRange","-clubSuitLengthRange","-heartSuitLengthRange","-diamondSuitLengthRange",
        "-spadeSuitHcpRange","-clubSuitHcpRange","-heartSuitHcpRange","-hcpRange","-cardsYes","-cardsNo","-cardType",
        "-longestSuit"]
        fullCardStr="AKQJT98765432"
        ln=len(wl)
        if wl[len(wl)-1]!="-end":
            print("Parse Error")
            print("The file should always end with '-end'")
            exit()
        while(ind<len(wl)):
            curkl=[]
            if wl[ind]=="-key":
                while(wl[ind]=="-key"):
    # =============================================================================
    #                 if ind+1>=ln:
    #                     print("Parse Error")
    #                     print("No key specified after keyword '-key' and abrupt end")
    #                     exit()
    # =============================================================================
                    keyVal=wl[ind+1]
                    if not(self.keyChecker(keyVal)):
                        print("Parse Error")
                        rc=lineAndWordNumber(ind+1,totLen)
                        print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        print("Key is invalid: "+keyVal)
                        exit()
                    curkl.append(wl[ind+1])
                    #Need to ensure that wl[ind+1] satisfies key convention
                    ind=ind+2
                curNode=BidNode(isConvention)
                curNode.bidSystem=bidSystemName

                while(wl[ind]!="-end"):
                    bidCat=None
                    bidCatInfo=None
                    bidDes=None
                    bidDesInfo=None
                    bidImp=None
                    bidImpInfo=None
                    if wl[ind]=="-bidCategory":
                        if wl[ind+1] not in bidCatList:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("Bid category "+ wl[ind+1]+ " not among the accepted categories ")
                            print(bidCatList)
                            exit()
                        else:
                            ind+=1
                            bidCat=wl[ind]
                            ind+=1
                            bidCatInfo=None
                            if wl[ind]=="-infoBegin":
                                ind+=1
                                bidCatInfo=""
                                while not(wl[ind]=="-infoEnd"):
                                    bidCatInfo+=wl[ind]+" "
                                    ind+=1
                                    if ind>=ln:
                                        print("Parse Error")
                                        print("-infoBegin should always be followed by -infoEnd")
                                        exit()
                                ind+=1
                            curNode.biddingCategory.categoryOfBid=bidCat
                            curNode.biddingCategory.info=bidCatInfo
                                        

                    elif wl[ind]=="-bidDescription":
                        if wl[ind+1] not in bidDesList:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("Bid description "+ wl[ind+1]+ " not among the accepted categories ")
                            print(bidDesList)
                            exit()
                        else:
                            ind+=1
                            bidDes=wl[ind]
                            curNode.biddingDescription.description=bidDes
                            bidDesInfo=""
                            
                            if bidDes == "Support":
                                ind+=1
                                if wl[ind] not in suitList:
                                    print("Parse Error")
                                    rc=lineAndWordNumber(ind,totLen)
                                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                                    print("Support should always be followed by suit and a count(number): "+ wl[ind]+ " not among the accepted suits ")
                                    print(suitList)
                                    exit()
                                curNode.biddingDescription.suit=wl[ind]
                                ind+=1
                                if not(wl[ind].isnumeric()):
                                    print("Parse Error")
                                    rc=lineAndWordNumber(ind,totLen)
                                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                                    print("Support suit should always be followed by a count: "+ wl[ind]+ " not among the accepted values ")
                                    exit()
                                supportVal=int(wl[ind])
                                if supportVal<0 or supportVal>13:
                                    print("Parse Error")
                                    rc=lineAndWordNumber(ind,totLen)
                                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                                    print("Support count "+wl[ind]+" not in bounds 0-13")
                                    exit()
                                curNode.biddingDescription.numCards=supportVal
                            if bidDes == "Cue" or bidDes == "CueFirstRound" or bidDes=="CueSecondRound":
                                ind+=1
                                if wl[ind] not in suitList:
                                    print("Parse Error")
                                    rc=lineAndWordNumber(ind,totLen)
                                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                                    print("Cues should always be followed by suit: "+ wl[ind]+ " not among the accepted suits ")
                                    print(suitList)
                                    exit()
                                curNode.biddingDescription.suit=wl[ind]
                            ind+=1
                            if wl[ind]=="-infoBegin":
                                ind+=1
                                bidDesInfo=""
                                while not(wl[ind]=="-infoEnd"):
                                    bidDesInfo+=wl[ind]+" "
                                    ind+=1
                                    if ind>=ln:
                                        print("Parse Error")
                                        print("-infoBegin should always be followed by -infoEnd")
                                        exit()
                                ind+=1
                                curNode.biddingDescription.info=bidDesInfo
                    elif wl[ind]=="-bidImpact":
                        if wl[ind+1] not in bidImpList:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("Bid Impact "+ wl[ind+1]+ " not among the accepted categories ")
                            print(bidImpList)
                            exit()
                        else:
                            ind+=1
                            curNode.bidImpact.bidImpactCategory=wl[ind]
                            ind+=1
                            if wl[ind]=="-infoBegin":
                                ind+=1
                                bidImpInfo=""
                                while not(wl[ind]=="-infoEnd"):
                                    bidImpInfo+=wl[ind]+" "
                                    ind+=1
                                    if ind>=ln:
                                        print("Parse Error")
                                        print("-infoBegin should always be followed by -infoEnd")
                                        exit()
                                ind+=1
                                curNode.bidImpact.info=bidImpInfo
                    
                    elif wl[ind]=="-spadeSuitLengthRange" or wl[ind]=="-clubSuitLengthRange" or wl[ind]=="-diamondSuitLengthRange" or wl[ind]=="-heartSuitLengthRange":
                        suitVal=wl[ind]
                        ind+=1
                        if not(wl[ind].isnumeric() and wl[ind+1].isnumeric()):
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-spadeSuitLengthRange should always be followed by 2 numbers: "+ wl[ind]+", "+wl[ind+1]+" not among the accepted values ")
                            exit()
                        lb=int(wl[ind])
                        ub=int(wl[ind+1])
                        if lb<0 or lb>13:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("lower bound value: "+str(lb)+" not in range 0-13")
                            exit()
                        if ub<0 or ub>13:
                            print("Parse error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+str(ub)+" not in range 0-13")
                            exit()
                        if lb>ub:
                            print("Parse error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+str(ub)+" less than lower bound value: "+lb)
                            exit()
                        curInd=-1
                        if suitVal=="-clubSuitLengthRange":
                            curInd=0
                        elif suitVal=="-diamondSuitLengthRange":
                            curInd=1
                        elif suitVal=="-heartSuitLengthRange":
                            curInd=2
                        elif suitVal=="-spadeSuitLengthRange":
                            curInd=3
                        else:
                            print("Logic error")
                            exit()
                        curNode.hand.suits[curInd].suitLength[0]=lb
                        curNode.hand.suits[curInd].suitLength[1]=ub
                        ind+=2
                        
                    elif wl[ind]=="-spadeSuitHcpRange" or wl[ind]=="-clubSuitHcpRange" or wl[ind]=="-diamondSuitHcpRange" or wl[ind]=="-heartSuitHcpRange":
                        suitVal=wl[ind]
                        ind+=1
                        if not(wl[ind].isnumeric() and wl[ind+1].isnumeric()):
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-spadeSuitLengthRange should always be followed by 2 numbers: "+ wl[ind]+", "+wl[ind+1]+" not among the accepted values ")
                            exit()
                        lb=int(wl[ind])
                        ub=int(wl[ind+1])
                        if lb<0 or lb>10:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("lower bound value: "+lb+" not in range 0-10")
                            exit()
                        if ub<0 or ub>10:
                            print("Parse error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+ub+" not in range 0-10")
                            exit()
                        if lb>ub:
                            print("Parse error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+ub+" less than lower bound value: "+lb)
                            exit()
                        curInd=-1
                        if suitVal=="-clubSuitHcpRange":
                            curInd=0
                        elif suitVal=="-diamondSuitHcpRange":
                            curInd=1
                        elif suitVal=="-heartSuitHcpRange":
                            curInd=2
                        elif suitVal=="-spadeSuitHcpRange":
                            curInd=3
                        else:
                            print("Logic error")
                            exit()
                        curNode.hand.suits[curInd].suitHcp[0]=lb
                        curNode.hand.suits[curInd].suitHcp[1]=ub
                        ind+=2
                    elif wl[ind]=="-hcpRange":
                        ind+=1
                        if not(wl[ind].isnumeric() and wl[ind+1].isnumeric()):
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-spadeSuitLengthRange should always be followed by 2 numbers: "+ wl[ind]+", "+wl[ind+1]+" not among the accepted values ")
                            exit()
                        lb=int(wl[ind])
                        ub=int(wl[ind+1])
                        if lb<0 or lb>37:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("lower bound value: "+str(lb)+" not in range 0-37")
                            exit()
                        if ub<0 or ub>37:
                            print("Parse error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+str(ub)+" not in range 0-37")
                            exit()
                        if lb>ub:
                            print("Parse error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("upper bound value: "+str(ub)+" less than lower bound value: "+lb)
                            exit()
                        curNode.hand.hcpBounds[0]=lb
                        curNode.hand.hcpBounds[1]=ub
                        ind+=2
                    elif wl[ind]=="-cardsYes" or wl[ind]=="-cardsNo":
                        aval=0
                        if wl[ind]=="-cardsYes":
                            aval=1
                        else:
                            aval=-1
                        ind+=1
                        suitInd=-1
                        if wl[ind] not in suitList:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-cardsYes should always be followed by a suit")
                            print("Entered suit: "+wl[ind]+" not in list of suits")
                            print(suitList)
                            exit()
                        suitInd=suitList.index(wl[ind])
                        ind+=1
                        cstr=wl[ind]
                        for char in cstr:
                            cardInd=fullCardStr.find(char)
                            if cardInd==-1:
                                print("Parse Error")
                                rc=lineAndWordNumber(ind,totLen)
                                print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                                print("The character: "+char+" in "+cstr+" is not a valid card")
                                print("Allowed values are: "+fullCardStr)
                                exit()
                            curNode.hand.suits[suitInd].cards[cardInd]=aval
                            
                        ind+=1
                    # Currently "balanced" is the only type supported
                    elif wl[ind]=="-cardType":
                        if wl[ind+1]!="balanced":
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-cardType should always be followed by balanced")
                            exit()
                        curNode.hand.suits[0].suitLength[0]=max(2,curNode.hand.suits[0].suitLength[0])
                        curNode.hand.suits[0].suitLength[1]=min(5,curNode.hand.suits[0].suitLength[1])
                        curNode.hand.suits[1].suitLength[0]=max(2,curNode.hand.suits[1].suitLength[0])
                        curNode.hand.suits[1].suitLength[1]=min(5,curNode.hand.suits[1].suitLength[1])
                        curNode.hand.suits[2].suitLength[0]=max(2,curNode.hand.suits[2].suitLength[0])
                        curNode.hand.suits[2].suitLength[1]=min(5,curNode.hand.suits[2].suitLength[1])
                        curNode.hand.suits[3].suitLength[0]=max(2,curNode.hand.suits[3].suitLength[0])
                        curNode.hand.suits[3].suitLength[1]=min(5,curNode.hand.suits[3].suitLength[1])
                        ind+=2
                    elif wl[ind]=="-longestSuit":
                        if wl[ind+1] not in suitList:
                            print("Parse Error")
                            rc=lineAndWordNumber(ind+1,totLen)
                            print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                            print("-longestSuit should always be followed by one of the  suits")
                            print(suitList)
                            exit()
                        curNode.hand.longestSuit=wl[ind+1]
                        ind+=2
                    else:
                        print("Parse Error")
                        rc=lineAndWordNumber(ind,totLen)
                        print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                        print("Wrong syntax used after the keys specified: "+wl[ind])
                        print("Allowed values are:")
                        print(keyValues)
                        exit()
                ind+=1
                curkl.sort(key=lambda x:len(x.split('-')))
                begString=curkl[0]
                if begString in bidDict:
                    print("Parse Error")
                    rc=lineAndWordNumber(ind-1,totLen)
                    print("Line: "+str(rc[0]))
                    print("Key: "+keyVal+" mentioned multiple times")
                    print("The key can only be defined once")
                    exit()
                bidDict[begString]=[curNode,1]

                for indVal in range(1,len(curkl)):
                    keyVal=curkl[indVal]
                    if keyVal in bidDict:
                        print("Parse Error")
                        rc=lineAndWordNumber(ind-1,totLen)
                        print("Line: "+str(rc[0]))
                        print("Key: "+keyVal+" mentioned multiple times")
                        print("The key can only be defined once")
                        exit()
                    bidDict[keyVal]=[begString,2]
            elif wl[ind]=="-convention":
                convName=wl[ind+1]
                if wl[ind+2]!="-conventionKey":
                    print("Parse Error")
                    rc=lineAndWordNumber(ind+2,totLen)
                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                        
                    print("Convention name cannot have any spaces")
                    print("-convention should always be followed by convention name[without spaces] followed by '-conventionKey'")
                    exit()
                ind+=3
                if wl[ind] in bidDict:
                    print("Parse Error")
                    rc=lineAndWordNumber(ind,totLen)
                    print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                    
                    print("Convention Key: "+keyVal+" mentioned multiple times")
                    print("The convention key can only be defined once")
                    exit()
                bidDict[wl[ind]]=[convName,3]
                ind+=2
            else:
                print("Parse Error")
                rc=lineAndWordNumber(ind,totLen)
                print("Line: "+str(rc[0])+" Word number: "+ str(rc[1]))
                    
                print("Rules can only be of 2 types")
                print("Rules of type1 should always start with '-key'")
                print("Rules of type2 should always start with '-convention'")
                print(wl[ind]+": Does not belong to both types")
                exit()

        # "All the lines have been parsed successfully and the nodes are stored in the dictionaries"
        print(bidDict)
        self.bidDict=bidDict
curParser=BidParser("neo4j","laasyaugrc")
curParser.parseBidLang("t4.txt","tr4")
curParser.df.deleteAllNodes("tr4")
curParser.graphCreator(curParser.bidDict,"tr4")


    



