import copy

from PyQt5 import QtCore, QtGui, QtWidgets

class SuitCards:
    def __init__(self):
        self.suitHcp=[0,10]
        self.suitLength=[0,13]
        
        #Cards of suit in order A,K,Q,T,9,...,2
        # 0:Maybe, 1:Yes, -1:No
        self.cards=[0]*13
        
    def __eq__(self, other): 
        
        if not isinstance(other, SuitCards):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.suitHcp == other.suitHcp and 
        self.suitLength == other.suitLength and self.cards==other.cards)

# this class is for a particular suit
# initally suitLength and suitHCP bounds are [0,13] and [0, 10] resp. Cards (all are maybe initially)

class PlayerHand:
    def __init__(self):
        self.hcpBounds=[0,37]
        self.totalPoints=[0,40]
        #Cards of holder in order of suits S,H,D,C
        self.suits=[SuitCards(),SuitCards(),SuitCards(),SuitCards()]
        # list of 4 SuitCards
    def __eq__(self, other):
        
        if not isinstance(other, PlayerHand):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.hcpBounds == other.hcpBounds and 
        self.totalPoints==other.totalPoints and self.suits == other.suits)
# total hcpBounds, totalPoints


class BidDescription:
    def __init__(self):
        #Description of bid
        #Like pre emptive or support or cue
        self.description="Custom"
        
        #If bid is supporting then Number of cards of support
        self.numCards=None
        
        #Suit type that is supported
        self.suit=None

        #Any additional information
        self.info=None

class BidCategory:
    def __init__(self):
        #Type of bid
        #Like opening, response, overcall, asking, respondingToAsk
        self.categoryOfBid="Custom"
        
        #If categoryOfBid is respondingToAsk then 
        #reference to askingBid node as key string
        #Otherwise any additional info
        self.info=None

class BidImpact:
    def __init__(self):
        self.bidImpactCategory="NonForcing"
        self.info=None

class BidNode:
    def __init__(self, isConv=False):
        #Forcing, non forcing, invitational, sign off
        self.bidImpact=BidImpact()
        
        #bidding convention this node is part of
        self.isConvention=isConv
        
        self.bidSystem=None
        self.bid=None
        self.parentbid=None
        self.forcing=False
        self.isParentForcing=False
        self.allowedBids=[True]*38
        #self.opening=False
        self.hand=PlayerHand()
        # self.parent = None
        # self.grandparent = None
        #################################################################################################
        # add all the player's hand (caution: this feature works only where the graph has not subtrees (it's only a tree and not a DAG) otherwise it doesn't give correct resutls)
        self.handsList = [PlayerHand(), PlayerHand(), PlayerHand(), PlayerHand()]
        self.isGameForcing = False
        self.isInvitational = False
        self.isParentInvitational = False
        self.trumpfit = "No"
        # self.isParentGameForcing = False
        ################################################################################################
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
        self.dictionary_contract_level = {None: None, "1C": "Part score", "2C":"Part score", "3C":"Part score", "4C":"Part score", "5C":"Game", "6C":"Small Slam", "7C":"Grand Slam",
                        "1D": "Part score", "2D":"Part score", "3D":"Part score", "4D":"Part score", "5D":"Game", "6D":"Small Slam", "7D":"Grand Slam", 
                        "1H": "Part score", "2H":"Part score", "3H":"Part score", "4H":"Game", "5H":"Game", "6H":"Small Slam", "7H":"Grand Slam",
                        "1S": "Part score", "2S":"Part score", "3S":"Part score", "4S":"Game", "5S":"Game", "6S":"small Slam", "7S":"Grand Slam",
                        "1NT": "Part score", "2NT":"Part score", "3NT":"Game", "4NT":"Game", "5NT":"Game", "6NT":"Small Slam", "7NT":"Grand Slam", "P":"None" }

    
    def getHandInfo(self,curNode):
        defaultHand=PlayerHand()
        if curNode==None:
            return defaultHand

        defaultHand.hcpBounds = [curNode['HcpLb'],curNode['HcpUb']]
        for i in range(4):
            defaultHand.suits[i].suitHcp = [curNode['SuitHcpLb'][i],curNode['SuitHcpUb'][i]]
            defaultHand.suits[i].suitLength = [curNode['SuitLengthLb'][i],curNode['SuitLengthUb'][i]]
            tmpList=curNode['SuitCards'][i*13:i*13+13]
            defaultHand.suits[i].cards = tmpList.copy()
        return defaultHand
# check what the curNode is and understand the function

    

    def createNode(self,curNode):
        errorString=None
        if not isinstance(curNode, BidNode):
            errorString="Given parameter is not of type BidNode"
            print(errorString)
            return [None,errorString]
        ptrNode=Node()
        # Node is the neo4j node
        self.graph.create(ptrNode)
        labelName=""
        if curNode.isConvention==True:
            labelName+="C_"
        else:
            labelName+="B_"
        print(labelName)
        print(curNode.isConvention)
        print(curNode.bidSystem)
        labelName+=curNode.bidSystem
        ptrNode.add_label(labelName)
        ptrNode['bidSystem']=curNode.bidSystem
        ptrNode['bid']=curNode.bid
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
        # need to add info for all 4 players hands
        # for now only one player hand information is stored
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
        ptrNode['isParentForcing']=curNode.isParentForcing
        ptrNode['isGameForcing']=curNode.isGameForcing
        ptrNode['isInvitational'] = curNode.isInvitational
        ptrNode['isParentInvitational'] = curNode.isParentInvitational
        ptrNode['Trump fit'] = curNode.trumpfit
        # ptrNode['Trump suit']="None"
        ptrNode['Parent bid'] = curNode.parentbid
        if ptrNode["isRoot"]==False:
            ptrNode['Contract level'] = self.dictionary_contract_level[ptrNode['bid']]
        # player hand - hcplb, hcpub, totalpointslb, totalpointsub, suits0, suits1, suits2, suits3
        ##############################################
        if curNode.handsList:
            for k in range(4):
                ptrNode['Player_'+str(k)+'_HCP_LB'] = curNode.handsList[k].hcpBounds[0]
                ptrNode['Player_'+str(k)+'_HCP_UB'] = curNode.handsList[k].hcpBounds[1]
                
                ptrNode['Player_'+str(k)+'Suit_C_lenLb'] = curNode.handsList[k].suits[0].suitLength[0]
                ptrNode['Player_'+str(k)+'Suit_C_lenUb'] = curNode.handsList[k].suits[0].suitLength[1]
                ptrNode['Player_'+str(k)+'Suit_D_lenLb'] = curNode.handsList[k].suits[1].suitLength[0]
                ptrNode['Player_'+str(k)+'Suit_D_lenUb'] = curNode.handsList[k].suits[1].suitLength[1]
                ptrNode['Player_'+str(k)+'Suit_H_lenLb'] = curNode.handsList[k].suits[2].suitLength[0]
                ptrNode['Player_'+str(k)+'Suit_H_lenUb'] = curNode.handsList[k].suits[2].suitLength[1]
                ptrNode['Player_'+str(k)+'Suit_S_lenLb'] = curNode.handsList[k].suits[3].suitLength[0]
                ptrNode['Player_'+str(k)+'Suit_S_lenUB'] = curNode.handsList[k].suits[3].suitLength[1]
                
                ptrNode['Player_'+str(k)+'Suit_C_HCPLb'] = curNode.handsList[k].suits[0].suitHcp[0]
                ptrNode['Player_'+str(k)+'Suit_C_HCPUb'] = curNode.handsList[k].suits[0].suitHcp[1]
                ptrNode['Player_'+str(k)+'Suit_D_HCPLb'] = curNode.handsList[k].suits[1].suitHcp[0]
                ptrNode['Player_'+str(k)+'Suit_D_HCPUb'] = curNode.handsList[k].suits[1].suitHcp[1]
                ptrNode['Player_'+str(k)+'Suit_H_HCPLb'] = curNode.handsList[k].suits[2].suitHcp[0]
                ptrNode['Player_'+str(k)+'Suit_H_HCPUb'] = curNode.handsList[k].suits[2].suitHcp[1]
                ptrNode['Player_'+str(k)+'Suit_S_HCPLb'] = curNode.handsList[k].suits[3].suitHcp[0]
                ptrNode['Player_'+str(k)+'Suit_S_HCPUB'] = curNode.handsList[k].suits[3].suitHcp[1]
                
                tlist = []
                for j in range(4):
                    tlist+=curNode.handsList[k].suits[j].cards
                ptrNode['Player_'+str(k)+'SuitCards'] = tlist
                ptrNode['Player_'+str(k)+'TotalPointsLb'] = curNode.handsList[k].totalPoints[0]
                ptrNode['Player_'+str(k)+'TotalPointsUb'] = curNode.handsList[k].totalPoints[1]
            ##############################################
        
        # print(type(ptrNode))
        return ptrNode

    def createRoot(self,bidSystemName,fl):
        #Create a bidNode with default values
        tmpNode=BidNode()
        tmpNode.bidSystem = bidSystemName
        print(f"in root {tmpNode.bidSystem}")
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
        rootNode['Forcing']=False
        rootNode['isParentForcing']=False
        rootNode['isInvitational']=False
        rootNode['isParentInvitational']=False
        rootNode['isGameForcing']=False
        rootNode['Parent bid'] = None
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
        # creates a neo4j node and adds to the database graph
        ###########################################################
        # here I should add the functionality to convert python info to neo4j info about all the hands of the players


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
            print(parentNode['AllowedBids'])
            print(cbid)
            print("A node with this bidvalue as child already exists")
            return None
        else:
            parentNode['AllowedBids'][cbid]=False
            childNode=self.createNode(bidNode)
            
            # Child Node is of neo4j type
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
            #####################################################################################
            if not bidNode.handsList:
                # when the node is a pass node

                for k in range(4):
                    childNode['Player_'+str(k)+'_HCP_LB'] = parentNode['Player_'+str(k)+'_HCP_LB'] 
                    childNode['Player_'+str(k)+'_HCP_UB'] = parentNode['Player_'+str(k)+'_HCP_UB']
                    # tlist = []
                    # for j in range(4):
                        # tlist+=curNode.handsList[k].suits[j].cards
                    childNode['Player_'+str(k)+'Suit_C_lenLb'] = parentNode['Player_'+str(k)+'Suit_C_lenLb']
                    childNode['Player_'+str(k)+'Suit_C_lenUb'] = parentNode['Player_'+str(k)+'Suit_C_lenUb']
                    childNode['Player_'+str(k)+'Suit_D_lenLb'] = parentNode['Player_'+str(k)+'Suit_D_lenLb']
                    childNode['Player_'+str(k)+'Suit_D_lenUb'] = parentNode['Player_'+str(k)+'Suit_D_lenUb']
                    childNode['Player_'+str(k)+'Suit_H_lenLb'] = parentNode['Player_'+str(k)+'Suit_H_lenLb']
                    childNode['Player_'+str(k)+'Suit_H_lenUb'] = parentNode['Player_'+str(k)+'Suit_H_lenUb']
                    childNode['Player_'+str(k)+'Suit_S_lenLb'] = parentNode['Player_'+str(k)+'Suit_S_lenLb']
                    childNode['Player_'+str(k)+'Suit_S_lenUB'] = parentNode['Player_'+str(k)+'Suit_S_lenUB']
                    
                    childNode['Player_'+str(k)+'Suit_C_HCPLb'] = parentNode['Player_'+str(k)+'Suit_C_HCPLb']
                    childNode['Player_'+str(k)+'Suit_C_HCPUb'] = parentNode['Player_'+str(k)+'Suit_C_HCPUb']
                    childNode['Player_'+str(k)+'Suit_D_HCPLb'] = parentNode['Player_'+str(k)+'Suit_D_HCPLb']
                    childNode['Player_'+str(k)+'Suit_D_HCPUb'] = parentNode['Player_'+str(k)+'Suit_D_HCPUb']
                    childNode['Player_'+str(k)+'Suit_H_HCPLb'] = parentNode['Player_'+str(k)+'Suit_H_HCPLb']
                    childNode['Player_'+str(k)+'Suit_H_HCPUb'] = parentNode['Player_'+str(k)+'Suit_H_HCPUb']
                    childNode['Player_'+str(k)+'Suit_S_HCPLb'] = parentNode['Player_'+str(k)+'Suit_S_HCPLb']
                    childNode['Player_'+str(k)+'Suit_S_HCPUB'] = parentNode['Player_'+str(k)+'Suit_S_HCPUB']
                    
                    childNode['Player_'+str(k)+'SuitCards'] = parentNode['Player_'+str(k)+'SuitCards']
                    childNode['Player_'+str(k)+'TotalPointsLb'] = parentNode['Player_'+str(k)+'TotalPointsLb']
                    childNode['Player_'+str(k)+'TotalPointsUb'] = parentNode['Player_'+str(k)+'TotalPointsUb']
            #####################################################################################
            childNode['Parent bid'] = parentNode['bid']
            if parentNode['Forcing']==True:
                childNode['isParentForcing']=True
            
            if parentNode['isParentForcing']==True and childNode['bid']=='P':
                childNode['comments'] = "Not valid since the partner's bid is forcing. "
            else:
                childNode['comments']="Valid bid. "
            
            if parentNode['isGameForcing']==True:
                childNode['isParentGameForcing']=True
            
            if parentNode['isParentGameForcing']==True:
                childNode['isGameForcing']=True
            
            if childNode['isGameForcing']==True and childNode['bid']=='P':
                childNode['comments'] = "Not valid since the partner's bid is Game forcing. "

            if parentNode['isInvitational']==True:
                childNode['isParentInvitational'] =True
            
            if parentNode['isParentInvitational']==True:
                if childNode['bid']=='P':
                    childNode['comments']+="Partner's invitation has been declined."
                else:
                    childNode['comments']+="Partner's invitation has been accepted."
            
            if childNode['Trump fit']=="Yes":
                childNode["Trump suit"]=parentNode['Parent bid'][1]
            # relationships = list(parentNode.relationships)
            print(childNode['Trump fit'])
            print(childNode['Trump suit'])
            # find the parent node
            # if len(relationships) > 0:
            #     first_relationship = relationships[0]
            #     grandparentNode = first_relationship.start_node if first_relationship.end_node == child_node else first_relationship.end_node
            # else:
            #     grandparentNode = None
            # if grandparent is not None:

            self.graph.push(childNode)
            self.graph.push(parentNode)
            bval="BidValue"
            el="edgeLabel"
            r=Relationship(parentNode,childNode)
            r['BidValue']=bidValue
            r[edgeLabel]=True
            self.graph.create(r)
            return childNode


    def insertChildWithOpPass(self,bidSystemName,bidNode,partnerNode,bidValue):
        # creates a neo4j node with an op pass (which means I have to do constraint propagation twice) and adds to the database graph
        ###########################################################
        # here I should add the functionality to convert python info to neo4j info about all the hands of the players

        
        if partnerNode==None:
            print("Partner node does not exist")
            return None
        edgeLabel="BidSystem_"+bidSystemName
        q0=("""match (x{nodeId:$val1})-[{BidValue:$val3,"""
            +edgeLabel+""":true}]->(n1) return n1""")
        
        passNode=self.graph.evaluate(q0,val1=partnerNode.identity,val3="P")
        # passBid=self.bidToInt["P"]
        # passNode=None
        # if partnerNode['AllowedBids'][passBid]==False:

        if passNode==None:
            opNode=BidNode()
            opNode.bid="P"
            opNode.bidSystem=bidSystemName
            #############################
            opNode.handsList = []
            
            #############################
            passNode=self.insertChild(bidSystemName,opNode,partnerNode,"P")
            # partnerNode['AllowedBids'][self.bidToInt["P"]]=False
    #     q1="""match (x{nodeId:$val1,bidSystem:$val2})-[{BidValue:$val3,"""+edgeLabel+""":true}]->(n1)
    #           return count(n1)"""
    #     co1=graph.evaluate(q1,val1=passNode.identity,val2=bidSystemName,val3=bidValue)
    #     if co1!=0:
    #         print("A node with this bid value as child already exists")
    #         return None
        finNode=self.insertChild(bidSystemName,bidNode,passNode,bidValue)
        return finNode

    def getChildren(self,bidSystemName,parentNode):
        if parentNode==None:
            return None
        edgeLabel="BidSystem_"+bidSystemName
        edgeLabel1="BidSystem_"+parentNode['bidSystem']
        # print("conv",edgeLabel1)
        q0=None
        if parentNode['isConvention']==False:
            q0="""match (x{nodeId:$val1})-[{"""+edgeLabel+""":true}]->(n1)
                  return (n1)"""
        else:
            q0="""match (n1)
                  match(x{nodeId:$val1})
                  where (x)-[{"""+edgeLabel+""":true}]->(n1) or 
                  (x)-[{"""+edgeLabel1+""":true}]->(n1)
                  return (n1)"""

        nodeCursor=self.graph.run(q0,val1=parentNode.identity)
        nodeRecordList=list(nodeCursor)
        nodeList=list(map(lambda x:x[0],nodeRecordList))
        return nodeList

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
        # q0="""match (x{nodeId:$val1})-[{BidValue:$val3,"""+edgeLabel+""":true}]->(n1)
        #     return count(n1)"""
        
        # co1=self.graph.evaluate(q0,val1=curNode.identity,val3=bidValue)
        # if co1!=0:
        #   print("A node with this bidvalue as child already exists")
        #   return False
        
        bidsAllowed=curNode['AllowedBids']
        cbid=self.bidToInt[bidValue]
        if bidsAllowed[cbid]==False:
            print(bidsAllowed)
            print(cbid)
            print("A node with this bidvalue as child already exists")
            return False
        curNode['AllowedBids'][cbid]=False
        self.graph.push(curNode)  
        r=Relationship(curNode,newChild)
        r['BidValue']=bidValue
        r[edgeLabel]=True
        self.graph.create(r)
        return True

    def deleteChild(self,bidSystemName,parentNode,childNode):
        #Just unlink if child node is a part of convention
        edgeLabel="BidSystem_"+bidSystemName
        if childNode['bidSystem']!=parentNode['bidSystem']:
            q0="""match (x{nodeId:$val1})-[rel{BidValue:$val3,"""+edgeLabel+""":true}]->(n1{nodeId:$val2})
                    delete rel"""
            self.graph.evaluate(q0,val1=parentNode.identity,val2=childNode.identity,val3=childNode['bid'])
            cbid=self.bidToInt[childNode['bid']]
            parentNode['AllowedBids'][cbid]=True
            self.graph.push(parentNode)
            return True
        

        #Check if the child node has more than 1 parent then also it can just be unlinked
        q1="""match (n)-[rel{"""+edgeLabel+""":true}]->(n1{nodeId:$val1})
                return count(n)"""
        co1=self.graph.evaluate(q1,val1=childNode.identity)
        if co1>1:
            q0="""match (x{nodeId:$val1})-[rel{BidValue:$val3,"""+edgeLabel+""":true}]->(n1{nodeId:$val2})
                    delete rel"""
            self.graph.evaluate(q0,val1=parentNode.identity,val2=childNode.identity,val3=childNode['bid'])
            cbid=self.bidToInt[childNode['bid']]
            parentNode['AllowedBids'][cbid]=True
            self.graph.push(parentNode)
            return True


        grChildList=self.getChildren(bidSystemName,childNode)
        
        #Child node is a leaf node
        if grChildList==None or len(grChildList)==0:
    #         q0="""match (x{nodeId:$val1})-[rel{BidValue:$val3,"""+edgeLabel+""":true}]->(n1{nodeId:$val2})
    #                 delete n1"""
    #         graph.evaluate(q0,val1=parentNode.identity,val2=childNode.identity,val3=childNode['bid'])
            cbid=self.bidToInt[childNode['bid']]
            parentNode['AllowedBids'][cbid]=True
            self.graph.delete(childNode)
            self.graph.push(parentNode)
            return True
        
        
        #Child node is not a leaf node
        print("Warning! Do you want to delete entire subtree rooted at child node")
        return False


    def deleteAllNodes(self,bidSystemName):
        q0="""match (x{bidSystem:$val})
               detach delete x"""
        self.graph.evaluate(q0,val=bidSystemName)

    def deleteChildRec(self,bidSystemName,curNode):
        edgeLabel="BidSystem_"+bidSystemName
        childList=self.getChildren(bidSystemName,curNode)
        for childNode in childList:
            if childNode['bidSystem']!=curNode['bidSystem']:
                q0="""match (x{nodeId:$val1})-[rel{BidValue:$val3,"""+edgeLabel+""":true}]->(n1{nodeId:$val2})
                        delete rel"""
                self.graph.evaluate(q0,val1=curNode.identity,val2=childNode.identity,val3=childNode['bid'])
            
            else:
                q1="""match (n)-[rel{"""+edgeLabel+""":true}]->(n1{nodeId:$val1})
                        return count(n)"""
                co1=self.graph.evaluate(q1,val1=childNode.identity)
                if co1>1:
                    q0="""match (x{nodeId:$val1})-[rel{BidValue:$val3,"""+edgeLabel+""":true}]->(n1{nodeId:$val2})
                            delete rel"""
                    self.graph.evaluate(q0,val1=curNode.identity,val2=childNode.identity,val3=childNode['bid'])
                
                else:
                    self.deleteChildRec(bidSystemName,childNode)
            
        self.graph.delete(curNode)


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

    def addConventionWithOpPass(self,bidSystemName,conventionName, partnerNode, bidValueList):
        if partnerNode==None:
            print("Partner node does not exist")
            return False
        edgeLabel="BidSystem_"+bidSystemName
        q0=("""match (x{nodeId:$val1})-[{BidValue:$val3,"""
            +edgeLabel+""":true}]->(n1) return n1""")
        
        passNode=self.graph.evaluate(q0,val1=partnerNode.identity,val3="P")
        # passBid=self.bidToInt["P"]
        # passNode=None
        # if partnerNode['AllowedBids'][passBid]==False:

        if passNode==None:
            opNode=BidNode()
            opNode.bid="P"
            opNode.bidSystem=bidSystemName
            passNode=self.insertChild(bidSystemName,opNode,partnerNode,"P")
            # partnerNode['AllowedBids'][self.bidToInt["P"]]=False
    #     q1="""match (x{nodeId:$val1,bidSystem:$val2})-[{BidValue:$val3,"""+edgeLabel+""":true}]->(n1)
    #           return count(n1)"""
    #     co1=graph.evaluate(q1,val1=passNode.identity,val2=bidSystemName,val3=bidValue)
    #     if co1!=0:
    #         print("A node with this bidvalue as child already exists")
    #         return None
        bval=self.addConvention(bidSystemName,conventionName, passNode, bidValueList)
        return bval

    def constraintPropagation(self,prevNodeHandList,curNodeHandList):
        errorString=None
        # If the variable values did not change then just return them
        if prevNodeHandList==curNodeHandList:
            return [curNodeHandList,errorString]
        #To avoid modifying contents of prev node and this node we create copies
        # The best updated contents from prev node and current node are taken.
        # A previous bid can convey 5+ spades and current bid can convey 3+ clubs.
        # So the best of both i.e. the 5+ spades and 3+ clubs needs to be set as initial values.
        flist=copy.deepcopy(curNodeHandList)
        for i in range(4):
            flist[i].hcpBounds[0]=max(curNodeHandList[i].hcpBounds[0],prevNodeHandList[i].hcpBounds[0])
            flist[i].hcpBounds[1]=min(curNodeHandList[i].hcpBounds[1],prevNodeHandList[i].hcpBounds[1])
            for j in range(4):
                flist[i].suits[j].suitHcp[0]=max(curNodeHandList[i].suits[j].suitHcp[0],prevNodeHandList[i].suits[j].suitHcp[0])
                flist[i].suits[j].suitHcp[1]=min(curNodeHandList[i].suits[j].suitHcp[1],prevNodeHandList[i].suits[j].suitHcp[1])
                flist[i].suits[j].suitLength[0]=max(curNodeHandList[i].suits[j].suitLength[0],prevNodeHandList[i].suits[j].suitLength[0])
                flist[i].suits[j].suitLength[1]=min(curNodeHandList[i].suits[j].suitLength[1],prevNodeHandList[i].suits[j].suitLength[1])
                for k in range(13):
                    if abs(curNodeHandList[i].suits[j].cards[k]>prevNodeHandList[i].suits[j].cards[k]):
                        flist[i].suits[j].cards[k]=curNodeHandList[i].suits[j].cards[k]
                    else:
                        flist[i].suits[j].cards[k]=prevNodeHandList[i].suits[j].cards[k]
                    
        updList=copy.deepcopy(flist)
        curList=copy.deepcopy(flist)
        fl=0
        if prevNodeHandList!=curNodeHandList:
            fl=1
        it=0
        # While the value of atleast 1 variable changes we need to repeatedly perform the constraint propagation
        while fl==1:
            it+=1

            #First lets propogate the effect on specific cards
            #Effect due to specific cards of other players

            #Cards in each suit
            for j in range(13):
                #Each suit
                for k in range(4):
                    
                    #Count of Yes
                    co1=0
                    #Count of No
                    co2=0
                    #Each player
                    for l in range(4):
                        if curList[l].suits[k].cards[j]==1:
                            co1=co1+1
                        elif curList[l].suits[k].cards[j]==-1:
                            co2=co2+1
                
                    if co1>1:
                        errorString=("Card "+str(j)+" suit "+
                                     str(k)+" is yes for more than 1 player")
                        print(errorString)
                        return [updList,errorString]
                    if co1==1:
                        for l in range(4):
                            #For all other players make that card as No.
                            if curList[l].suits[k].cards[j]!=1:
                                updList[l].suits[k].cards[j]=-1
                    
                    if co2==4:
                        errorString=("Card "+str(j)+" suit "+
                                     str(k)+" is No for all 4 players")
                        print(errorString)
                        return [updList,errorString]
                    if co2==3:
                        for l in range(4):
                            #For the only player with not of no make that card as yes.
                            if curList[l].suits[k].cards[j]!=-1:
                                updList[l].suits[k].cards[j]=1
            
            #Effect due to suit HCP
            #For each player
            for j in range(4):
                #For each suit
                for k in range(4):
                    #No special cards
                    if curList[j].suits[k].suitHcp[1]<1:
                        updList[j].suits[k].cards[0]=-1
                        updList[j].suits[k].cards[1]=-1
                        updList[j].suits[k].cards[2]=-1
                        updList[j].suits[k].cards[3]=-1
                    
                    #Only J allowed
                    elif curList[j].suits[k].suitHcp[1]<2:
                        updList[j].suits[k].cards[0]=-1
                        updList[j].suits[k].cards[1]=-1
                        updList[j].suits[k].cards[2]=-1
                        
                    #Only J,Q allowed
                    elif curList[j].suits[k].suitHcp[1]<3:
                        updList[j].suits[k].cards[0]=-1;
                        updList[j].suits[k].cards[1]=-1;

                    #Only A not allowed
                    elif curList[j].suits[k].suitHcp[1]<4:
                        updList[j].suits[k].cards[0]=-1
                    
                    #All special cards must be present
                    if curList[j].suits[k].suitHcp[0]>9:
                        updList[j].suits[k].cards[0]=1
                        updList[j].suits[k].cards[1]=1
                        updList[j].suits[k].cards[2]=1
                        updList[j].suits[k].cards[3]=1
                    
                    #Only J may not be present
                    elif curList[j].suits[k].suitHcp[0]>8:
                        updList[j].suits[k].cards[0]=1;
                        updList[j].suits[k].cards[1]=1;
                        updList[j].suits[k].cards[2]=1;
                        
                    #Only J,Q may not be present
                    elif curList[j].suits[k].suitHcp[0]>7:
                        updList[j].suits[k].cards[0]=1;
                        updList[j].suits[k].cards[1]=1;

                    #A must be present
                    elif curList[j].suits[k].suitHcp[0]>6:
                        updList[j].suits[k].cards[0]=1
                        

            #Suit length and total hcp do not effect specific cards directly
            
            
            #Propogation of effect on suit length
            
            #Effect of other suits suit length

            #Sum of cards of all suits for a player=13
            # Lower bound for a suit length >= 13 - Sum of Upper bound of suit length of other suits.
            # Upper bound for a suit length <= 13 - Sum of Lower bound of suit length of other suits.
            
            #Each player
            for j in range(4):
                #Each suit
                for k in range(4):
                    upboundsum=0;
                    lpboundsum=0;
                    for l in range(4):
                        if l!=k:
                            lpboundsum+=curList[j].suits[l].suitLength[0]
                            upboundsum+=curList[j].suits[l].suitLength[1]
                            
                    updList[j].suits[k].suitLength[0]=(
                        max(updList[j].suits[k].suitLength[0],13-upboundsum))
                    updList[j].suits[k].suitLength[1]=(
                        min(updList[j].suits[k].suitLength[1],13-lpboundsum))
                    
            
            #Effect of other players suit length
            # Sum of total cards of a suit = 13
            # – Lower bound for that suit length>=13- Sum of Upper bound of that suit length
            # of other players.
            # – Upper bound for that suit length <= 13 – Sum of Lower bound of suit length of
            # other players.
            
            #For each suit
            for j in range(4):
                #For each player
                for k in range(4):
                    upboundsum=0;
                    lpboundsum=0;
                    for l in range(4):
                        if l!=k:
                            lpboundsum+=curList[l].suits[j].suitLength[0]
                            upboundsum+=curList[l].suits[j].suitLength[1]
                            
                    updList[k].suits[j].suitLength[0]=(
                    max(updList[k].suits[j].suitLength[0],13-upboundsum))
                    updList[k].suits[j].suitLength[1]=(
                    min(updList[k].suits[j].suitLength[1],13-lpboundsum))

            
            #Effect of specific cards of the player
            
            #For each player
            for j in range(4):
                #For each suit
                for k in range(4):
                    lb=0
                    ub=0
                    for l in range(13):
                        if curList[j].suits[k].cards[l]==1:
                            lb=lb+1
                        elif curList[j].suits[k].cards[l]==-1:
                            ub+=1
                    updList[j].suits[k].suitLength[0]=(
                    max(updList[j].suits[k].suitLength[0],lb))
                    updList[j].suits[k].suitLength[1]=(
                    min(updList[j].suits[k].suitLength[1],13-ub))
            
            #Effect of suit hcp
            
            #For each Player
            for j in range(4):
                #For each Suit
                for k in range(4):
                    if curList[j].suits[k].suitHcp[0]>9:
                        updList[j].suits[k].suitLength[0]=(
                        max(updList[j].suits[k].suitLength[0],4))
                    elif curList[j].suits[k].suitHcp[0]>7:
                        updList[j].suits[k].suitLength[0]=(
                        max(updList[j].suits[k].suitLength[0],3))
                    elif curList[j].suits[k].suitHcp[0]>4:
                        updList[j].suits[k].suitLength[0]=(
                        max(updList[j].suits[k].suitLength[0],2))
                    elif curList[j].suits[k].suitHcp[0]>0:
                        updList[j].suits[k].suitLength[0]=(
                        max(updList[j].suits[k].suitLength[0],1))
                    
                    if curList[j].suits[k].suitHcp[1]<1:
                        updList[j].suits[k].suitLength[1]=(
                        min(updList[j].suits[k].suitLength[1],9))
                    elif curList[j].suits[k].suitHcp[1]<3:
                        updList[j].suits[k].suitLength[1]=(
                        min(updList[j].suits[k].suitLength[1],10))
                    elif curList[j].suits[k].suitHcp[1]<6:
                        updList[j].suits[k].suitLength[1]=(
                        min(updList[j].suits[k].suitLength[1],11))
                    elif curList[j].suits[k].suitHcp[1]<10:
                        updList[j].suits[k].suitLength[1]=(
                        min(updList[j].suits[k].suitLength[1],12))
                        
            #Propogation of suit hcp
            #Effect of other suits hcp and total hcp
            
            """The upper and lower bound on each suit HCP are affected by the total HCP and vice
            versa.
            – Lower bound for that suit HCP >= Lower bound on Total HCP -Sum of Upper
            bound of suit HCP of other suits.
            – Upper bound for that suit HCP <= Upper bound on Total HCP – Sum of Lower
            bound of suit HCP of other suits."""
            

            #For each player
            for j in range(4):
                #For each suit
                for k in range(4):
                    lb=0;
                    ub=0;
                    for l in range(4):
                        if k!=l:
                            lb+=curList[j].suits[l].suitHcp[0]
                            ub+=curList[j].suits[l].suitHcp[1]
                    updList[j].suits[k].suitHcp[0]=(
                    max(updList[j].suits[k].suitHcp[0],
                        curList[j].hcpBounds[0]-ub))
                    updList[j].suits[k].suitHcp[1]=(
                    min(updList[j].suits[k].suitHcp[1],
                        curList[j].hcpBounds[1]-lb))

                    
            #Effect of other players suit hcp
            """Sum of HCP of a suit across all players = 10
            – Lower bound for that suit HCP>=10 - Sum of Upper bound of that suit HCP of
            other players.
            – Upper bound for that suit HCP <= 10 – Sum of Lower bound of suit HCP of
            other players."""

            #For each suit
            for j in range(4):

                #For each player
                for k in range(4):
                    lb=0;
                    ub=0;
                    for l in range(4):
                        if l!=k:
                            lb+=curList[l].suits[j].suitHcp[0]
                            ub+=curList[l].suits[j].suitHcp[1]
                    updList[k].suits[j].suitHcp[0]=(
                    max(updList[k].suits[j].suitHcp[0],
                        10-ub))
                    updList[k].suits[j].suitHcp[1]=(
                    min(updList[k].suits[j].suitHcp[1],
                        10-lb))
            
            #Effect of specific cards
            
            #For each player
            for j in range(4):

                #For each suit
                for k in range(4):
                    #Special cards
                    lb=0;
                    ub=0;
                    for l in range(4):
                        if curList[j].suits[k].cards[l]==1:
                            lb+=4-l;
                        elif curList[j].suits[k].cards[l]==-1:
                            ub+=4-l;

                    updList[j].suits[k].suitHcp[0]=(
                    max(updList[j].suits[k].suitHcp[0],
                        lb))
                    updList[j].suits[k].suitHcp[1]=(
                    min(updList[j].suits[k].suitHcp[1],
                        10-ub))

            
            #Effect of suit length
            
            #For each player
            for j in range(4):
                #For each suit
                for k in range(4):
                    #Suit length
                    if curList[j].suits[k].suitLength[0]>12:
                        updList[j].suits[k].suitHcp[0]=(
                        max(updList[j].suits[k].suitHcp[0],10))
                    elif curList[j].suits[k].suitLength[0]>11:
                        updList[j].suits[k].suitHcp[0]=(
                        max(updList[j].suits[k].suitHcp[0],6))
                    elif curList[j].suits[k].suitLength[0]>10:
                        updList[j].suits[k].suitHcp[0]=(
                        max(updList[j].suits[k].suitHcp[0],3))
                    elif curList[j].suits[k].suitLength[0]>9:
                        updList[j].suits[k].suitHcp[0]=(
                        max(updList[j].suits[k].suitHcp[0],1))
                    
                    
                    if curList[j].suits[k].suitLength[1]<4:
                        updList[j].suits[k].suitHcp[1]=(
                        min(updList[j].suits[k].suitHcp[1],9))
                    elif curList[j].suits[k].suitLength[1]<3:
                        updList[j].suits[k].suitHcp[1]=(
                        min(updList[j].suits[k].suitHcp[1],7))
                    elif curList[j].suits[k].suitLength[1]<2:
                        updList[j].suits[k].suitHcp[1]=(
                        min(updList[j].suits[k].suitHcp[1],4))
                    elif curList[j].suits[k].suitLength[1]<1:
                        updList[j].suits[k].suitHcp[1]=(
                        min(updList[j].suits[k].suitHcp[1],0))
                    
            #Propogation of total hcp
            
            #Effect of other players hcp
            
            """Sum of Total HCP across all players = 40
            – Lower bound for a player HCP >= 40 - Sum of Upper bound of other players
            HCP.
            – Upper bound for a player HCP <= 40 - Sum of Lower bound of other players
            HCP."""

            for j in range(4):
                lb=0
                ub=0
                for k in range(4):
                    if j!=k:
                        lb+=curList[k].hcpBounds[0]
                        ub+=curList[k].hcpBounds[1]
                
                updList[j].hcpBounds[0]=(
                max(updList[j].hcpBounds[0],40-ub))
                updList[j].hcpBounds[1]=(
                min(updList[j].hcpBounds[1],40-lb))
                
            
            #Effect of specific cards
            
            
            #For each player
            for j in range(4):
                lb=0
                ub=0
                for k in range(4):
                    for l in range(4):
                        if curList[j].suits[k].cards[l]==1:
                            lb+=4-l
                        elif curList[j].suits[k].cards[l]==-1:
                            ub+=4-l

                updList[j].hcpBounds[0]=(
                max(updList[j].hcpBounds[0],lb))
                updList[j].hcpBounds[1]=(
                min(updList[j].hcpBounds[1],40-ub))
            
            #Check for all types of consistency in the updList
            #consistentFlag=0
            
            #Suit Lengths and Suit HCPs
            #Sum of lower bounds of all suit lengths<=13
            #Sum of upper bounds of all suit lengths>=13
            #For each suit sum of all players suit length lower bound<=13
            #For each suit sum of all players suit length upper bound>=13
            
            #Sum of lower bounds of all suit Hcps<=10
            #Sum of upper bounds of all suit Hcps>=10
            #For each suit sum of all players suit HCP lower bound<=10
            #For each suit sum of all players suit HCP upper bound>=10
            
            #After all the updates performed above the upper and lower bound check is sufficient
            #Upper bound>=Lower bound
            
            for j in range(4):
    #             lblenpersuit=0
    #             ublenpersuit=0
    #             lblenperplayer=0
    #             ublenperplayer=0
                
    #             lbhcppersuit=0
    #             ubhcppersuit=0
    #             lbhcpperplayer=0
    #             ubhcpperplayer=0
                if updList[j].hcpBounds[1]<updList[j].hcpBounds[0]:
                    errorString=("Player "+str(j)+" Total Hcp Upper bound less than lower bound")
                    print(errorString)
                    return [updList,errorString]
                for k in range(4):
                    if updList[j].suits[k].suitLength[1]<updList[j].suits[k].suitLength[0]:
                        errorString=("Player "+str(j)+" suit "+str(k)+
                                     " suitLength Upper bound less than lower bound")
                        print(errorString)
                        return [updList,errorString]
                    
                    if updList[j].suits[k].suitHcp[1]<updList[j].suits[k].suitHcp[0]:
                        errorString=("Player "+str(j)+" suit "+
                                     str(k)+" suitHcp Upper bound less than lower bound")
                        print(errorString)
                        return [updList,errorString]
     
            if curList==updList:
                fl=0
            curList=copy.deepcopy(updList)
        # print("Iteration count: ",it) 
        return [updList,errorString]


class CurrentMenu:
    def __init__(self,graph):
        self.graph=graph
        self.systemName=None
        self.systemType=None
        self.rootNode=None

class CurrentState:

    def __init__(self, bidSystemN ,graphName,MWobj,convList,convBidDict):
        df=DAGFunctions(graphName)
        self.curSeq = ""
        self.conventionList=convList
        self.conventionBidDict=convBidDict
        self.currentNode = df.findRoot(bidSystemN)
        # neo4j node
        self.bidSystemName = bidSystemN
        self.pathLength = 0
        self.curNodeHandList = [PlayerHand(), PlayerHand(), PlayerHand(), PlayerHand()]
        self.prevNodeHandList = [PlayerHand(), PlayerHand(), PlayerHand(), PlayerHand()]
        self.currentChildren = df.getChildren(bidSystemN,self.currentNode)
        self.graph=graphName
        self.MainWindowObj=MWobj
        self.MainWindowObj.comboBoxSelectChild.clear()
        bidList=list(map(lambda x : x['bid'], self.currentChildren))
        cbList=["None"]
        cbList+=bidList
        my_string = ','.join(map(str, bidList))
        self.MainWindowObj.textEditCurrentChildren.setPlainText(my_string)
        self.MainWindowObj.comboBoxSelectChild.clear()
        self.MainWindowObj.comboBoxSelectChild.addItems(cbList)

    def updateNode(self,newBidSequence):
        df=DAGFunctions(self.graph)
        curNode=df.findNode(self.bidSystemName,newBidSequence)
        if curNode!=None:
            self.curSeq=newBidSequence
            self.currentNode=curNode
            self.currentChildren=df.getChildren(self.bidSystemName,curNode)
            self.MainWindowObj.textEditCurrentSequence.setPlainText(newBidSequence)
            bidList=list(map(lambda x : x['bid'], self.currentChildren))
            cbList=["None"]
            cbList+=bidList
            my_string = ','.join(map(str, bidList))
            self.MainWindowObj.textEditCurrentChildren.setPlainText(my_string)
            self.MainWindowObj.comboBoxSelectChild.clear()
            self.MainWindowObj.comboBoxSelectChild.addItems(cbList)
    def updateChildren(self,childrenList):
        self.currentChildren=childrenList
        bidList=list(map(lambda x : x['bid'], childrenList))
        cbList=["None"]
        cbList+=bidList
        my_string = ','.join(map(str, bidList))
        self.MainWindowObj.textEditCurrentChildren.setPlainText(my_string)
        self.MainWindowObj.comboBoxSelectChild.clear()
        self.MainWindowObj.comboBoxSelectChild.addItems(cbList)

class SpecialComboBox:
    def __init__(self,Dialog,xpos,ypos,fl,defaultValue,suitType,bval):
        self.cdialog=Dialog
        self.comboBox=QtWidgets.QComboBox(Dialog)
        # if bval==False:
        #     self.comboBox.color_effect.setEnabled(False)
        self.comboBox.setEnabled(bval)
        if bval==False:
                self.comboBox.setStyleSheet('QComboBox {background-color: black; color: white}')
        if fl==1:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,41,21))
            for i in range(14):
                self.comboBox.addItem(str(i))
            self.comboBox.setCurrentIndex(defaultValue[suitType])
            
        
        elif fl==2:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,41,21))
            
            for i in range(11):
                self.comboBox.addItem(str(i))
            self.comboBox.setCurrentIndex(defaultValue[suitType])
            
        elif fl==3:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,41,21))
            for i in range(38):
                self.comboBox.addItem(str(i))
            self.comboBox.setCurrentIndex(defaultValue[suitType])
            

        elif fl==4:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,111,25))
            categoryOfBidList = ["Custom", "Opening", "Response", "Overcall", "Asking", "RespondingToAsk"]
            self.comboBox.addItems(categoryOfBidList)
            self.comboBox.setCurrentIndex(categoryOfBidList.index(defaultValue[0]))

        elif fl==5:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,111,25))
            impactOfBidList= ["NonForcing","Forcing","Invitational","GameForcing",
            "GameInvitational","SlamInvitational","SignOff","Custom"]
            self.comboBox.addItems(impactOfBidList)
            self.comboBox.setCurrentIndex(impactOfBidList.index(defaultValue[0]))

        elif fl==6:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,111,25))
            # self.comboBox.addItem("None")
            #Need to update this with a variable from main window
            bidDescriptionList= ["Custom","Preemptive","Support","Cue","Cue_first_round","Cue_second_round"]
            self.comboBox.addItems(bidDescriptionList)
            
            self.comboBox.setCurrentIndex(bidDescriptionList.index(defaultValue[0]))

        elif fl==7:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,111,25))
            self.comboBox.addItem("None")
            #Need to update this with a variable from main window
            SupportSuitList= ["Clubs","Diamonds","Hearts","Spades"]
            self.comboBox.addItems(SupportSuitList)
            if defaultValue[0]==0:
                self.comboBox.setCurrentIndex(defaultValue[0])
            else:
                self.comboBox.setCurrentIndex(SupportSuitList.index(defaultValue[0])+1)
        elif fl==8:
            self.comboBox.setGeometry(QtCore.QRect(xpos,ypos,111,25))
            self.comboBox.addItem("None")
            #Need to update this with a variable from main window
            SupportCountList= ["0","1","2","3","4","5","6","7","8","9","10","11","12","13"]
            self.comboBox.addItems(SupportCountList)
            
            if defaultValue[0]==0:
                self.comboBox.setCurrentIndex(defaultValue[0])
            else:
                self.comboBox.setCurrentIndex(SupportCountList.index(defaultValue[0])+1)
        ###############################################################################################################
        elif fl==9:
            self.comboBox.setGeometry(QtCore.QRect(xpos, ypos, 111, 25))
            # self.comboBox.addItem("None")
            trumpfit = ["Yes", "No"]
            self.comboBox.addItems(trumpfit)
            self.comboBox.setCurrentIndex(1)
        ###############################################################################################################

    # def retranslateComboBox(self,fl):
    #     _translate = QtCore.QCoreApplication.translate
    #     if fl==1:
    #         for i in range(14):
    #             self.comboBox.setItemText(i,_translate("Dialog",str(i)))

    #     elif fl==2:
    #         for i in range(11):
    #             self.comboBox.setItemText(i,_translate("Dialog",str(i)))
        
    #     elif fl==3:
    #         for i in range(38):
    #             self.comboBox.setItemText(i,_translate("Dialog",str(i)))
        
    #     elif fl==4:
    #         typeOfBidList = ["Opening", "Response", "Overcall", "Asking", "RespondingToAsk", "Custom"]
    #         for i in range(len(typeOfBidList)):
    #             self.comboBox.setItemText(i,_translate("Dialog",typeOfBidList[i]))
        
    #     elif fl==5:
    #         impactOfBidList= ["NonForcing","Forcing","Invitational",
    #         "GameInvitational","SlamInvitational","SignOff","Custom"]
    #         for i in range(len(impactOfBidList)):
    #             self.comboBox.setItemText(i,_translate("Dialog",impactOfBidList[i]))
        
    #     elif fl==6:
    #         conventionList= ["Stayman","Smolen","Custom","None"]
    #         for i in range(len(conventionList)):
    #             self.comboBox.setItemText(i,_translate("Dialog",conventionList[i]))
                
class cardsComboBoxList:
    def __init__(self,Dialog,xpos,ypos,defaultValueList,curSuit,bval):
        self.cdialog=Dialog
        
        self.cardsList=[None]*13
        itemList=["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
        optionList=["Maybe","Yes","No"]
        for i in range(13):
            self.cardsList[i]=QtWidgets.QComboBox(Dialog)
            # if bval==False:
            #     self.cardsList[i].color_effect.setEnabled(False)
            self.cardsList[i].setEnabled(bval)
            # self.cardsList[i].setStyleSheet('QComboBox {background-color: red}')
            if bval==False:
                self.cardsList[i].setStyleSheet('QComboBox {background-color: black; color: white}')
            self.cardsList[i].setGeometry(QtCore.QRect(xpos,ypos+i*30,91,25))
            for j in range(3):
                self.cardsList[i].addItem(itemList[i]+"-"+optionList[j])
            
            self.cardsList[i].setCurrentIndex((defaultValueList[i+13*curSuit]+3)%3)
            
    # def retranslatecardList(self):
    #     _translate = QtCore.QCoreApplication.translate
    #     itemList=["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
    #     optionList=["Maybe","Yes","No"]
    #     for i in range(13):
    #         for j in range(3):
    #             self.cardsList[i].setItemText(j,_translate("Dialog",itemList[i]+"-"+optionList[j]))

class UiDialogBidInfo(object):

    def setupUi(self, Dialog,currentStateobj,MWobj,bid,fltemp,ptrNode,bval):
        Dialog.setModal(True)
        Dialog.setObjectName("Bid Info")
        Dialog.resize(727, 562)
        bidT=bid
        if bid==None:
            bidT="root"
        Dialog.setWindowTitle("Node info for child bid "+bidT)
        self.currentState=currentStateobj
        self.MainWindowobj=MWobj
        self.bid=bid
        self.fl=fltemp
        self.ptrNode=ptrNode
        self.suitLengthLbCBList=[None]*4
        self.suitLengthUbCBList=[None]*4
        self.suitHcpLbCBList=[None]*4
        self.suitHcpUbCBList=[None]*4
        self.suitCardsCBList=[None]*4
        curHand=self.currentState.curNodeHandList[(self.currentState.pathLength-1)%4]
        # print(curHand.hcpBounds)
        # print(curHand.suits[0].suitLength)
        for i in range(4):
            if bval==True:
                self.suitLengthLbCBList[i]=SpecialComboBox(Dialog,50,50+i*40,1,ptrNode['SuitLengthLb'],i,bval)
                self.suitLengthUbCBList[i]=SpecialComboBox(Dialog,100,50+i*40,1,ptrNode['SuitLengthUb'],i,bval)
                self.suitHcpLbCBList[i]=SpecialComboBox(Dialog,160,50+i*40,2,ptrNode['SuitHcpLb'],i,bval)
                self.suitHcpUbCBList[i]=SpecialComboBox(Dialog,210,50+i*40,2,ptrNode['SuitHcpUb'],i,bval)
                self.suitCardsCBList[i]=cardsComboBoxList(Dialog,270+i*100,70,ptrNode['SuitCards'],i,bval)
            else:
                self.suitLengthLbCBList[i]=SpecialComboBox(Dialog,50,50+i*40,1,curHand.suits[i].suitLength,0,bval)
                self.suitLengthUbCBList[i]=SpecialComboBox(Dialog,100,50+i*40,1,curHand.suits[i].suitLength,1,bval)
                self.suitHcpLbCBList[i]=SpecialComboBox(Dialog,160,50+i*40,2,curHand.suits[i].suitHcp,0,bval)
                self.suitHcpUbCBList[i]=SpecialComboBox(Dialog,210,50+i*40,2,curHand.suits[i].suitHcp,1,bval)
                self.suitCardsCBList[i]=cardsComboBoxList(Dialog,270+i*100,70,curHand.suits[i].cards,0,bval)    
        if bval==False:
            self.totalHcpLbCB=SpecialComboBox(Dialog,110,220,3,curHand.hcpBounds,0,bval)
            self.totalHcpUbCB=SpecialComboBox(Dialog,170,220,3,curHand.hcpBounds,1,bval)
        else:
            self.totalHcpLbCB=SpecialComboBox(Dialog,110,220,3,[ptrNode['HcpLb']],0,bval)
            self.totalHcpUbCB=SpecialComboBox(Dialog,170,220,3,[ptrNode['HcpUb']],0,bval)
        self.bidCategoryCB=SpecialComboBox(Dialog,130,280,4,[ptrNode['bidCategory']],0,bval)
        self.bidImpactCB=SpecialComboBox(Dialog,130,320,5,[ptrNode['bidImpact']],0,bval)
        self.bidDescriptionCB=SpecialComboBox(Dialog,130,360,6,[ptrNode['bidDescription']],0,bval)
        if ptrNode['supportOrCueSuit']!=None:
            self.bidSupportSuitCB=SpecialComboBox(Dialog,130,400,7,[ptrNode['supportOrCueSuit']],0,bval)
        else:
            self.bidSupportSuitCB=SpecialComboBox(Dialog,130,400,7,[0],0,bval)
        
        if ptrNode['supportCount']!=None:
            self.bidSupportCountCB=SpecialComboBox(Dialog,130,440,8,[str(ptrNode['supportCount'])],0,bval)
        else:
            self.bidSupportCountCB=SpecialComboBox(Dialog,130,440,8,[0],0,bval)
        
        self.trumpfit = SpecialComboBox(Dialog, 370, 480, 9, [ptrNode['Trump fit']], 0, bval)
        
        
        
        self.labelSuit = QtWidgets.QLabel(Dialog)
        self.labelSuit.setGeometry(QtCore.QRect(10, 10, 31, 16))
        self.labelSuit.setObjectName("labelSuit")
        self.labelSuitC = QtWidgets.QLabel(Dialog)
        self.labelSuitC.setGeometry(QtCore.QRect(10, 50, 21, 16))
        self.labelSuitC.setObjectName("labelSuitC")
        self.labelSuitD = QtWidgets.QLabel(Dialog)
        self.labelSuitD.setGeometry(QtCore.QRect(10, 90, 21, 16))
        self.labelSuitD.setObjectName("labelSuitD")
        self.labelSuitH = QtWidgets.QLabel(Dialog)
        self.labelSuitH.setGeometry(QtCore.QRect(10, 130, 21, 16))
        self.labelSuitH.setObjectName("labelSuitH")
        self.labelSuitS = QtWidgets.QLabel(Dialog)
        self.labelSuitS.setGeometry(QtCore.QRect(10, 170, 21, 16))
        self.labelSuitS.setObjectName("labelSuitS")
        self.labelLength = QtWidgets.QLabel(Dialog)
        self.labelLength.setGeometry(QtCore.QRect(70, 10, 51, 16))
        self.labelLength.setObjectName("labelLength")
        self.labelHCP = QtWidgets.QLabel(Dialog)
        self.labelHCP.setGeometry(QtCore.QRect(190, 10, 31, 16))
        self.labelHCP.setObjectName("labelHCP")
        self.labelCards = QtWidgets.QLabel(Dialog)
        self.labelCards.setGeometry(QtCore.QRect(440, 10, 41, 16))
        self.labelCards.setObjectName("labelCards")
        self.labelTotalHCP = QtWidgets.QLabel(Dialog)
        self.labelTotalHCP.setGeometry(QtCore.QRect(20, 220, 71, 17))
        self.labelTotalHCP.setObjectName("labelTotalHCP")
        
        self.labelSuitC1 = QtWidgets.QLabel(Dialog)
        self.labelSuitC1.setGeometry(QtCore.QRect(300, 40, 21, 16))
        self.labelSuitC1.setObjectName("labelSuitC1")
        self.labelSuitD1 = QtWidgets.QLabel(Dialog)
        self.labelSuitD1.setGeometry(QtCore.QRect(400, 40, 21, 16))
        self.labelSuitD1.setObjectName("labelSuitD1")
        self.labelSuitH1 = QtWidgets.QLabel(Dialog)
        self.labelSuitH1.setGeometry(QtCore.QRect(500, 40, 21, 16))
        self.labelSuitH1.setObjectName("labelSuitH1")
        self.labelSuitS1 = QtWidgets.QLabel(Dialog)
        self.labelSuitS1.setGeometry(QtCore.QRect(600, 40, 21, 16))
        self.labelSuitS1.setObjectName("labelSuitS1")
        
        self.labelBidC = QtWidgets.QLabel(Dialog)
        self.labelBidC.setGeometry(QtCore.QRect(20, 280, 111, 17))
        self.labelBidC.setObjectName("labelBidC")
        self.labelBidT = QtWidgets.QLabel(Dialog)
        self.labelBidT.setGeometry(QtCore.QRect(20, 320, 111, 17))
        self.labelBidT.setObjectName("labelBidT")
        self.labelDes = QtWidgets.QLabel(Dialog)
        self.labelDes.setGeometry(QtCore.QRect(20, 360, 111, 17))
        self.labelDes.setObjectName("labelDes")

        self.labelSupSuit = QtWidgets.QLabel(Dialog)
        self.labelSupSuit.setGeometry(QtCore.QRect(20, 400, 111, 17))
        self.labelSupSuit.setObjectName("labelSupSuit")
        self.labelSupSuit.setText("Support/Cue Suit")
        self.labelSupCount = QtWidgets.QLabel(Dialog)
        self.labelSupCount.setGeometry(QtCore.QRect(20, 440, 111, 17))
        self.labelSupCount.setObjectName("labelSupSuit")
        self.labelSupCount.setText("Support Count")
        self.labelAskingKey = QtWidgets.QLabel(Dialog)
        self.labelAskingKey.setGeometry(QtCore.QRect(20, 480, 111, 17))
        self.labelAskingKey.setObjectName("labelAskingKey")
        self.labelAskingKey.setText("Asking Key")
        self.labelSupCount.setText("Support Count")
        self.textEditAskingkey = QtWidgets.QTextEdit(Dialog)
        self.textEditAskingkey.setGeometry(QtCore.QRect(130, 480, 131, 41))
        ######################################################################
        
        self.labeltrumpfit = QtWidgets.QLabel(Dialog)
        self.labeltrumpfit.setGeometry(QtCore.QRect(270, 480, 111, 17))
        self.labeltrumpfit.setObjectName('Trump fit')
        self.labeltrumpfit.setText("Trump fit")
        

        ######################################################################
        self.textEditAskingkey.setObjectName("textEditAskingkey")
        self.pushButtonSubmit = QtWidgets.QPushButton(Dialog)
        self.pushButtonSubmit.setGeometry(QtCore.QRect(600, 510, 89, 25))
        self.pushButtonSubmit.setObjectName("pushButtonSubmit")
        self.pushButtonCancel = QtWidgets.QPushButton(Dialog)
        self.pushButtonCancel.setGeometry(QtCore.QRect(480, 510, 89, 25))
        self.pushButtonCancel.setObjectName("pushButtonCancel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.pushButtonSubmit.clicked.connect(lambda:self.submitClicked(Dialog,self))
        self.pushButtonCancel.clicked.connect(lambda:self.cancelClicked(Dialog))
        Dialog.exec()

    def submitClicked(self,Dialog,bInfo):
        curNode=BidNode()
        curNode.bidImpact.bidImpactCategory=bInfo.bidImpactCB.comboBox.currentText()
        # print(curNode.bidImpact)
        #name of bid like stayman,smolen,jacoby etc.
        # curNode.bidName=None
        
        #bidding convention this node is part of
        # curNode.convention=bInfo.bidConventionCB.comboBox.currentText()
        # print(curNode.convention)
        curNode.bidSystem=self.currentState.bidSystemName
        curNode.trumpfit = self.trumpfit.comboBox.currentText()
        curNode.bid=bInfo.bid
        curNode.forcing=False
        if curNode.bidImpact.bidImpactCategory=="Forcing" or curNode.bidImpact.bidImpactCategory=="GameForcing":
            curNode.forcing=True
        if curNode.bidImpact.bidImpactCategory=="GameForcing":
            curNode.isGameForcing = True
        if curNode.bidImpact.bidImpactCategory=="Invitational":
            curNode.isInvitational = True
        curNode.signOff=False
        if curNode.bidImpact.bidImpactCategory=="SignOff":
            curNode.signOff=True
        
        curNode.allowedBids=[True]*38

        

        curNode.hand=PlayerHand()

        curNode.hand.hcpBounds[0]=int(bInfo.totalHcpLbCB.comboBox.currentText())
        curNode.hand.hcpBounds[1]=int(bInfo.totalHcpUbCB.comboBox.currentText())
        
        

        for j in range(4):
            curNode.hand.suits[j].suitHcp[0]=int(bInfo.suitHcpLbCBList[j].comboBox.currentText())
            curNode.hand.suits[j].suitHcp[1]=int(bInfo.suitHcpUbCBList[j].comboBox.currentText())
            curNode.hand.suits[j].suitLength[0]=int(bInfo.suitLengthLbCBList[j].comboBox.currentText())
            curNode.hand.suits[j].suitLength[1]=int(bInfo.suitLengthUbCBList[j].comboBox.currentText())
            for k in range(13):
                valTemp=int(bInfo.suitCardsCBList[j].cardsList[k].currentIndex())
                if valTemp==2:
                    valTemp=-1
                curNode.hand.suits[j].cards[k]=valTemp
            # print("Cards ",curNode.hand.suits[j].cards)
            # print("Le ",curNode.hand.suits[j].suitLength)
        curNode.biddingCategory=BidCategory()
        curNode.biddingCategory.categoryOfBid=bInfo.bidCategoryCB.comboBox.currentText()
        if curNode.biddingCategory.categoryOfBid=="RespondingToAsk":
            curNode.biddingCategory.info=bInfo.textEditAskingkey.toPlainText()
        
        curNode.biddingDescription=BidDescription()
        curNode.biddingDescription.description=bInfo.bidDescriptionCB.comboBox.currentText()
        
        if curNode.biddingDescription.description=="Support":
            curNode.biddingDescription.suit=bInfo.bidSupportSuitCB.comboBox.currentText()
            curNode.biddingDescription.numCards=int(bInfo.bidSupportCountCB.comboBox.currentText())
        
        if curNode.biddingDescription.description=="Cue" or curNode.biddingDescription.description=="Cue_second_round" or curNode.biddingDescription.description=="Cue_first_round":
            curNode.biddingDescription.suit=bInfo.bidSupportSuitCB.comboBox.currentText()

        # doing constraint propagation for all hands
        ################################################################
        prevList = self.currentState.curNodeHandList
        newList = copy.deepcopy(self.currentState.curNodeHandList)
        newList[(self.currentState.pathLength)%4] = curNode.hand
        finalList = DAGFunctions(self.currentState.graph).constraintPropagation(prevList, newList)
        curNode.handsList = finalList[0]
        ###############################################################
        obj=DAGFunctions(self.currentState.graph)
        bsname=self.currentState.bidSystemName
        if self.fl==1:
            # add child
            
            obj.insertChild(bsname,curNode,self.currentState.currentNode,bInfo.bid)
            nodeList=obj.getChildren(bsname,self.currentState.currentNode)
            self.currentState.updateChildren(nodeList)
            
            # self.currentState.currentChildren=nodeList
            # bidList=list(map(lambda x : x['bid'], nodeList))
            # my_string = ','.join(map(str, bidList))
            # bInfo.MainWindowobj.textEdit1.setPlainText(my_string)
        if self.fl==2:
            # add child with op pass
            obj.insertChildWithOpPass(bsname,curNode,self.currentState.currentNode,bInfo.bid)
            nodeList=obj.getChildren(bsname,self.currentState.currentNode)
            self.currentState.updateChildren(nodeList)

        if self.fl==3:
            # modify the current node info here
            # so whatever I add at insertChild place I need to add it here too
            self.currentState.currentNode['SuitLengthLb']=[curNode.hand.suits[0].suitLength[0],
                                     curNode.hand.suits[1].suitLength[0],
                                     curNode.hand.suits[2].suitLength[0],
                                     curNode.hand.suits[3].suitLength[0]]
            
            self.currentState.currentNode['SuitLengthUb']=[curNode.hand.suits[0].suitLength[1],
                                     curNode.hand.suits[1].suitLength[1],
                                     curNode.hand.suits[2].suitLength[1],
                                     curNode.hand.suits[3].suitLength[1]]
            
            self.currentState.currentNode['SuitHcpLb']=[curNode.hand.suits[0].suitHcp[0],
                                  curNode.hand.suits[1].suitHcp[0],
                                  curNode.hand.suits[2].suitHcp[0],
                                  curNode.hand.suits[3].suitHcp[0]]
            
            self.currentState.currentNode['SuitHcpUb']=[curNode.hand.suits[0].suitHcp[1],
                                  curNode.hand.suits[1].suitHcp[1],
                                  curNode.hand.suits[2].suitHcp[1],
                                  curNode.hand.suits[3].suitHcp[1]]
            
            self.currentState.currentNode['HcpLb']=curNode.hand.hcpBounds[0]
            self.currentState.currentNode['HcpUb']=curNode.hand.hcpBounds[1]
            # print("hi ",self.currentState.currentNode['HcpUb'])
            tmpList=[]
            for j in range(4):
                tmpList+=curNode.hand.suits[j].cards
            self.currentState.currentNode['SuitCards']=tmpList
            self.currentState.currentNode['TotalPointsLb']=curNode.hand.totalPoints[0]
            self.currentState.currentNode['TotalPointsUb']=curNode.hand.totalPoints[1]
            self.currentState.currentNode['Forcing']=curNode.forcing
            self.currentState.currentNode['ParentForcing'] = curNode.isParentForcing
            self.currentState.currentNode['isGameForcing'] = curNode.isGameForcing
            # ptrNode['AllowedBids']=curNode.allowedBids
            self.currentState.currentNode['bidImpact']=curNode.bidImpact.bidImpactCategory
            self.currentState.currentNode['bidCategory']=curNode.biddingCategory.categoryOfBid
            self.currentState.currentNode['bidDescription']=curNode.biddingDescription.description
            self.currentState.currentNode['askingKey']=curNode.biddingCategory.info
            self.currentState.currentNode['supportOrCueSuit']=curNode.biddingDescription.suit
            self.currentState.currentNode['supportCount']=curNode.biddingDescription.numCards
            # self.currentState.currentNode['isRoot']=False
            # obj.graph.merge(self.ptrNode)
            #############################################################
            for k in range(4):
                self.currentState.currentNode['Player_'+str(k)+'_HCP_LB'] = curNode.handsList[k].hcpBounds[0]
                self.currentState.currentNode['Player_'+str(k)+'_HCP_UB'] = curNode.handsList[k].hcpBounds[1]
                tlist = []
                for j in range(4):
                    tlist+=curNode.handsList[k].suits[j].cards
                for j in range(4):
                    if j==0:
                        x='C'
                    elif j==1:
                        x='D'
                    elif j==2:
                        x='H'
                    elif j==3:
                        x='S'
                    self.currentState.currentNode['Player_'+str(k)+'Suit_'+x+'_lenLb'] = curNode.handsList[k].suits[j].suitLength[0]
                    self.currentState.currentNode['Player_'+str(k)+'Suit_'+x+'_lenUb'] = curNode.handsList[k].suits[j].suitLength[1]
                    self.currentState.currentNode['Player_'+str(k)+'Suit_'+x+'_HCPLb'] = curNode.handsList[k].suits[j].suitHcp[0]
                    self.currentState.currentNode['Player_'+str(k)+'Suit_'+x+'_HCPUb'] = curNode.handsList[k].suits[j].suitHcp[1]
                    
                self.currentState.currentNode['Player_'+str(k)+'SuitCards'] = tlist
                self.currentState.currentNode['Player_'+str(k)+'TotalPointsLb'] = curNode.handsList[k].totalPoints[0]
                self.currentState.currentNode['Player_'+str(k)+'TotalPointsUb'] = curNode.handsList[k].totalPoints[1]
            ##############################################################
            
            obj.graph.push(self.currentState.currentNode)
            # self.currentState.currentNode=self.ptrNode
            # ptrNode['highestIncomingBid']=-1
            # ptrNode['nodeId']=ptrNode.identity

            # self.currentState.currentChildren=nodeList
            # bidList=list(map(lambda x : x['bid'], nodeList))
            # my_string = ','.join(map(str, bidList))
            # bInfo.MainWindowobj.textEdit1.setPlainText(my_string)
        # print("Des ",curNode.biddingDescription.description)
        Dialog.close()
    
    def cancelClicked(self,Dialog):
        Dialog.close()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        # Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        
        # for i in range(4):
        #     self.suitLengthLbCBList[i].retranslateComboBox(1)
        #     self.suitLengthUbCBList[i].retranslateComboBox(1)
        #     self.suitHcpLbCBList[i].retranslateComboBox(2)
        #     self.suitHcpUbCBList[i].retranslateComboBox(2)
        #     self.suitCardsCBList[i].retranslatecardList()

        # self.totalHcpLbCB.retranslateComboBox(3)
        # self.totalHcpUbCB.retranslateComboBox(3)
        
        # self.bidTypeCB.retranslateComboBox(4)
        # self.bidImpactCB.retranslateComboBox(5)
        # self.bidConventionCB.retranslateComboBox(6)

        self.labelSuit.setText(_translate("Dialog", "Suit"))
        self.labelSuitC.setText(_translate("Dialog", "C"))
        self.labelSuitD.setText(_translate("Dialog", "D"))
        self.labelSuitH.setText(_translate("Dialog", "H"))
        self.labelSuitS.setText(_translate("Dialog", "S"))
        self.labelLength.setText(_translate("Dialog", "Length"))
        self.labelHCP.setText(_translate("Dialog", "HCP"))
        self.labelCards.setText(_translate("Dialog", "Cards"))
        self.labelTotalHCP.setText(_translate("Dialog", "Total HCP"))
        
        self.labelSuitC1.setText(_translate("Dialog", "C"))
        self.labelSuitD1.setText(_translate("Dialog", "D"))
        self.labelSuitH1.setText(_translate("Dialog", "H"))
        self.labelSuitS1.setText(_translate("Dialog", "S"))
        
        self.labelBidC.setText(_translate("Dialog", "Bid Category"))
        
        self.labelBidT.setText(_translate("Dialog", "Bid Type"))
        # self.labelCon.setText(_translate("Dialog", "Convention"))
        
        self.labelDes.setText(_translate("Dialog", "Bid Description"))
        self.pushButtonSubmit.setText(_translate("Dialog", "Submit"))
        self.pushButtonCancel.setText(_translate("Dialog", "Cancel"))



class BidPushButton:

    def __init__(self,currentStateObj,MWobj,Dialog,i,j,fl,bval):
        self.bidNameList=["C","D","H","S","NT"]
        self.fl=fl
        self.curPushButton=QtWidgets.QPushButton(Dialog)
        self.curPushButton.setGeometry(QtCore.QRect(j*80, i*40, 81, 41))
        self.curPushButton.setObjectName("pushButton"+str(i+1)+self.bidNameList[j])
        self.curPushButton.setEnabled(bval)
        self.currentState=currentStateObj
        self.MainWindowObj=MWobj
        self.curPushButton.clicked.connect(lambda:self.buttonClickedBid(self.curPushButton.text()))
        self.dialogBox=Dialog

    def retranslateButton(self,Dialog,i,j):
        _translate = QtCore.QCoreApplication.translate
        self.curPushButton.setText(_translate("Dialog", str(i+1)+self.bidNameList[j]))


    # def connectButton(self):
    #     self.curPushButton.clicked.connect(lambda:self.buttonClickedBid(self.curPushButton.text()))

    def buttonClickedBid(self,bid):
        # bid=bidButton.geometry()
        # print(bid)
        # obj=DAGFunctions(self.currentState.graph)
        # bsname=self.currentState.bidSystemName
        # obj.insertChild(bsname,BidNode(),self.currentState.currentNode,bid)
        # nodeList=obj.getChildren(bsname,self.currentState.currentNode)
        # bidList=list(map(lambda x : x['bid'], nodeList))
        # my_string = ','.join(map(str, bidList))
        # self.MainWindowObj.textEdit1.setPlainText(my_string)
        Dialog = QtWidgets.QDialog()
        ui = UiDialogBidInfo()
        df=DAGFunctions(self.currentState.graph)
        cNode=BidNode()
        cNode.bidSystem=self.currentState.bidSystemName
        cNode.bid=bid
        tmpNode=df.createNode(cNode)
        ui.setupUi(Dialog,self.currentState,self.MainWindowObj,bid,self.fl,tmpNode,True)
        # self.curDialog.close()
        self.dialogBox.close()

class GoToNodeDialog(object):
    def setupUi(self, Dialog,currentStateobj,MWobj,fl):
        Dialog.setModal(True)
        Dialog.setObjectName("GoToNodeDialog")
        Dialog.resize(400, 300)
        Dialog.setWindowTitle("Bid Sequence")
        self.fl=fl
        self.curDialog=Dialog
        self.currentState=currentStateobj
        self.MainWindowobj=MWobj
        self.textEditBidSequence = QtWidgets.QTextEdit(Dialog)
        self.textEditBidSequence.setGeometry(QtCore.QRect(30, 40, 201, 70))
        self.textEditBidSequence.setObjectName("textEditBidSequence")
        self.lineEditErrorMessage = QtWidgets.QLineEdit(Dialog)
        self.lineEditErrorMessage.setGeometry(QtCore.QRect(50, 150, 291, 25))
        self.lineEditErrorMessage.setObjectName("lineEditErrorMessage")
        self.pushButtonGoToNode = QtWidgets.QPushButton(Dialog)
        self.pushButtonGoToNode.setGeometry(QtCore.QRect(250, 50, 101, 25))
        self.pushButtonGoToNode.setObjectName("pushButtonGoToNode")
        self.labelBidSequence = QtWidgets.QLabel(Dialog)
        self.labelBidSequence.setGeometry(QtCore.QRect(40, 10, 141, 17))
        self.labelBidSequence.setObjectName("labelBidSequence")
        self.pushButtonGoToNode.clicked.connect(self.pushButtonGoToNodeClicked)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        # Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        # self.lineEdit.setText(_translate("Dialog", "The bid sequence entered does not exist"))
        if self.fl==1:
            self.pushButtonGoToNode.setText(_translate("Dialog", "Go To Node"))
        elif self.fl==2:
            self.pushButtonGoToNode.setText(_translate("Dialog", "Add Subtree"))    
        self.labelBidSequence.setText(_translate("Dialog", "Enter Bid Sequence"))

    def pushButtonGoToNodeClicked(self):
        bidSeq=self.textEditBidSequence.toPlainText()
        df=DAGFunctions(self.currentState.graph)
        curNode=df.findNode(self.currentState.bidSystemName,bidSeq)
        if curNode==None:
            self.lineEditErrorMessage.setText("The bid sequence entered does not exist")
            # self.lineEditErrorMessage.adjustSize()
        else:
            if self.fl==1:
                self.currentState.updateNode(bidSeq)
                self.curDialog.close()
            elif self.fl==2:
                ptrNode=self.currentState.currentNode 
                bidValue=curNode['bid']
                bidpos=df.bidToInt[bidValue]
                if ptrNode==curNode:
                    self.lineEditErrorMessage.setText("The subtree is same as current node")
                if ptrNode['AllowedBids'][bidpos]==False:
                    self.lineEditErrorMessage.setText("The subtree cannot be added due to bid conflict")

                else:
                    # ptrNode['AllowedBids'][bidpos]=False
                    df.addSubtree(self.currentState.bidSystemName,ptrNode,curNode)
                    childNodeList=df.getChildren(self.currentState.bidSystemName,ptrNode)
                    self.currentState.updateChildren(childNodeList)
                    self.curDialog.close()


class BidCheckBox:
    def __init__(self,currentStateobj,Dialog,i,j,fl):
        self.bidNameList=["C","D","H","S","NT"]
        self.currentState=currentStateobj
        self.curDialog=Dialog
        self.checkBox = QtWidgets.QCheckBox(Dialog)
        self.checkBox.setGeometry(QtCore.QRect(j*40, i*20, 40, 20))
        self.checkBox.setText(str(i+1)+self.bidNameList[j])
        self.checkBox.setEnabled(fl)

class UiDialogCheckBoxBids(object):
    def setupUi(self, Dialog,currentStateobj,conventionName,fl):
        Dialog.setModal(True)
        Dialog.setObjectName("BidCBDialog")
        Dialog.setWindowTitle("Choice of Opening bids")
        self.curDialog=Dialog
        self.fl=fl
        Dialog.resize(260,200)
        self.currentState=currentStateobj
        self.conventionName=conventionName
        self.curBidList=self.currentState.conventionBidDict[conventionName]
        self.df=DAGFunctions(self.currentState.graph)
        self.bidBool=[False]*38
        nodeToCheck=self.currentState.currentNode
        if self.fl==False:
            pBid=None
            for j1 in range(len(self.currentState.currentChildren)):
                if self.currentState.currentChildren[j1]['bid']=="P":
                    pBid=self.currentState.currentChildren[j1]
                    break
            nodeToCheck=pBid
        for j in range(len(self.curBidList)):
            valCheck=self.df.bidToInt[self.curBidList[j]]
            if nodeToCheck==None or nodeToCheck['AllowedBids'][valCheck]:
                self.bidBool[valCheck]=True


        self.checkBoxList=[None]*38
        for i in range(7):
            for j in range(5):
                self.checkBoxList[i*5+j]=BidCheckBox(self.currentState,Dialog,i,j,self.bidBool[i*5+j])

        self.checkBoxList[35]=QtWidgets.QCheckBox(Dialog)
        self.checkBoxList[35].setGeometry(QtCore.QRect(0, 140, 40, 20))
        self.checkBoxList[35].setText("P")
        self.checkBoxList[35].setEnabled(self.bidBool[35])

        self.checkBoxList[36]=QtWidgets.QCheckBox(Dialog)
        self.checkBoxList[36].setGeometry(QtCore.QRect(40, 140, 40, 20))
        self.checkBoxList[36].setText("Dbl")
        self.checkBoxList[36].setEnabled(self.bidBool[36])

        self.checkBoxList[37]=QtWidgets.QCheckBox(Dialog)
        self.checkBoxList[37].setGeometry(QtCore.QRect(80, 140, 60, 20))
        self.checkBoxList[37].setText("ReDbl")
        self.checkBoxList[37].setEnabled(self.bidBool[37])

        self.pushButtonSubmit=QtWidgets.QPushButton(Dialog)
        self.pushButtonSubmit.setGeometry(QtCore.QRect(160, 160, 81, 31))
        self.pushButtonSubmit.setText("Submit")
        self.pushButtonSubmit.clicked.connect(self.pushButtonSubmitClicked)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec()


    def pushButtonSubmitClicked(self):
        finalBidList=[]
        for j in range(35):
            if self.checkBoxList[j].checkBox.isChecked():
                finalBidList.append(self.checkBoxList[j].checkBox.text())
        if self.checkBoxList[35].isChecked():
            finalBidList.append(self.checkBoxList[35].text())
        if self.checkBoxList[36].isChecked():
            finalBidList.append(self.checkBoxList[36].text())
        if self.checkBoxList[37].isChecked():
            finalBidList.append(self.checkBoxList[37].text())
        
        if len(finalBidList)==0:
            self.curDialog.close()
        else:
            if self.fl==True:
                self.df.addConvention(self.currentState.bidSystemName,self.conventionName,self.currentState.currentNode,finalBidList)
            if self.fl==False:
                self.df.addConventionWithOpPass(self.currentState.bidSystemName,self.conventionName,self.currentState.currentNode,finalBidList)
            
            nodeList=self.df.getChildren(self.currentState.bidSystemName,self.currentState.currentNode)
            self.currentState.updateChildren(nodeList)
            self.curDialog.close()

class UiDialogAddConvention(object):
    def setupUi(self, Dialog,currentStateobj,fl):
        # Dialog.setModal(True)
        Dialog.setObjectName("AddConventionDialog")
        Dialog.resize(400,300)
        Dialog.setWindowTitle("Add Convention")
        self.curDialog=Dialog
        self.fl=fl
        self.currentState=currentStateobj
        self.labelConventionName=QtWidgets.QLabel(Dialog)
        self.labelConventionName.setGeometry(QtCore.QRect(20,60,140,25))
        self.labelConventionName.setObjectName("labelConventionName")
        self.comboBox=QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(190,60,140,25))
        self.comboBox.setObjectName("comboBoxConvention")
        self.comboBox.addItems(self.currentState.conventionList)
        self.pushButtonSubmit=QtWidgets.QPushButton(Dialog)
        self.pushButtonSubmit.setGeometry(QtCore.QRect(280,240,89,25))
        self.pushButtonSubmit.setObjectName("pushButtonSubmit")
        self.pushButtonSubmit.setText("Submit")
        self.labelConventionName.setText("Choose Convention")
        self.pushButtonSubmit.clicked.connect(lambda:self.pushButtonSubmitClicked(self.comboBox.currentText()))
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec()

    def pushButtonSubmitClicked(self,conventionName):
        Dialog = QtWidgets.QDialog()
        ui = UiDialogCheckBoxBids()
        ui.setupUi(Dialog,self.currentState,conventionName,self.fl)
        self.curDialog.close()


class UiDialogDeleteConvention(object):
    def setupUi(self, Dialog,currentStateobj):
        Dialog.setModal(True)
        Dialog.setObjectName("DeleteConventionDialog")
        Dialog.resize(400,300)
        Dialog.setWindowTitle("Delete Convention")
        self.curDialog=Dialog
        self.currentState=currentStateobj
        self.labelConventionName=QtWidgets.QLabel(Dialog)
        self.labelConventionName.setGeometry(QtCore.QRect(20,60,140,25))
        self.labelConventionName.setObjectName("labelConventionName")
        self.comboBox=QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(190,60,140,25))
        self.comboBox.setObjectName("comboBoxConvention")
        self.comboBox.addItems(self.currentState.conventionList)
        self.pushButtonSubmit=QtWidgets.QPushButton(Dialog)
        self.pushButtonSubmit.setGeometry(QtCore.QRect(280,240,89,25))
        self.pushButtonSubmit.setObjectName("pushButtonSubmit")
        self.pushButtonSubmit.setText("Submit")
        self.labelConventionName.setText("Choose Convention")
        self.pushButtonSubmit.clicked.connect(lambda:self.pushButtonSubmitClicked(self.comboBox.currentText()))
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.exec()

    def pushButtonSubmitClicked(self,conventionName):

        Dialog = QtWidgets.QDialog()
        ui = UiDialogCheckBoxBids()
        ui.setupUi(Dialog,self.currentState,conventionName)
        self.curDialog.close()

class BidDialog(object):
    def setupUi(self, Dialog,currentStateobj,MWobj,fl):
        Dialog.setModal(True)
        Dialog.setObjectName("BidDialog")
        Dialog.resize(402, 331)
        Dialog.setWindowTitle("Choose bid")
        self.curDialog=Dialog
        self.currentState=currentStateobj
        self.MainWindowobj=MWobj
        self.pushButtonList=[None]*38
        self.fl=fl
        # bidNameList=["C","D","H","S","NT"]

        for i in range(7):
            for j in range(5):
                if self.fl==1:
                    bval=self.currentState.currentNode['AllowedBids'][i*5+j]
                if self.fl==2:
                    #Check if pass is child of current node
                    # If yes then its allowed bids
                    #If no then all bids.
                    bval=True
                    highIncomeBid=self.currentState.currentNode['highestIncomingBid']
                    if i*5+j<=highIncomeBid:
                        bval=False
                    pBid=None
                    for j1 in range(len(self.currentState.currentChildren)):
                        if self.currentState.currentChildren[j1]['bid']=="P":
                            pBid=self.currentState.currentChildren[j1]
                            break
                    if pBid!=None:
                        bval=pBid['AllowedBids'][i*5+j]
                self.pushButtonList[i*5+j]=BidPushButton(self.currentState,self.MainWindowobj,Dialog,i,j,fl,bval)
        

        self.pushButtonList[35]=QtWidgets.QPushButton(Dialog)
        self.pushButtonList[35].setGeometry(QtCore.QRect(0, 280, 81, 41))
        self.pushButtonList[35].setObjectName("pushButtonP")
        self.pushButtonList[35].setEnabled(self.currentState.currentNode['AllowedBids'][35])
        self.pushButtonList[35].clicked.connect(lambda:self.buttonClickedBid(self.pushButtonList[35].text()))

        self.pushButtonList[36]=QtWidgets.QPushButton(Dialog)
        self.pushButtonList[36].setGeometry(QtCore.QRect(80, 280, 81, 41))
        self.pushButtonList[36].setObjectName("pushButtonDbl")
        self.pushButtonList[36].setEnabled(self.currentState.currentNode['AllowedBids'][36])
        self.pushButtonList[36].clicked.connect(lambda:self.buttonClickedBid(self.pushButtonList[36].text()))
        
        self.pushButtonList[37]=QtWidgets.QPushButton(Dialog)
        self.pushButtonList[37].setGeometry(QtCore.QRect(160, 280, 81, 41))
        self.pushButtonList[37].setObjectName("pushButtonReDbl")
        self.pushButtonList[37].setEnabled(self.currentState.currentNode['AllowedBids'][37])
        self.pushButtonList[37].clicked.connect(lambda:self.buttonClickedBid(self.pushButtonList[37].text()))
        

        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        Dialog.exec()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        # Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        # bidNameList=["C","D","H","S","NT"]
        for i in range(0,7):
            for j in range(0,5):
                self.pushButtonList[i*5+j].retranslateButton(Dialog,i,j)
                # print(self.pushButtonList[i*5+j].text())
        self.pushButtonList[35].setText(_translate("Dialog", "P"))
        self.pushButtonList[36].setText(_translate("Dialog", "Dbl"))
        self.pushButtonList[37].setText(_translate("Dialog", "ReDbl"))
        
        

    def buttonClickedBid(self,bid):
        # bid=bidButton.geometry()
        # print(bid)
        # obj=DAGFunctions(self.currentState.graph)
        # bsname=self.currentState.bidSystemName
        # obj.insertChild(bsname,BidNode(),self.currentState.currentNode,bid)
        # nodeList=obj.getChildren(bsname,self.currentState.currentNode)
        # bidList=list(map(lambda x : x['bid'], nodeList))
        # my_string = ','.join(map(str, bidList))
        # self.MainWindowobj.textEdit1.setPlainText(my_string)
        Dialog = QtWidgets.QDialog()
        ui = UiDialogBidInfo()
        cNode=BidNode()
        cNode.bidSystem=self.currentState.bidSystemName
        df=DAGFunctions(self.currentState.graph)
        tmpNode=df.createNode(cNode)
        ui.setupUi(Dialog,self.currentState,self.MainWindowobj,bid,self.fl,tmpNode,True)
        self.curDialog.close()


class ChooseSystem(object):
    def setupUi(self,Dialog,curMenu,fl):
        Dialog.setModal(True)
        Dialog.setObjectName("chooseSystemDialog")
        Dialog.resize(400, 300)
        Dialog.setWindowTitle("Choice of Bidding System or Convention")
        self.fl=fl
        self.currentMenu=curMenu
        self.curDialog=Dialog
        self.pushButtonSubmit=QtWidgets.QPushButton(Dialog)
        self.pushButtonSubmit.setGeometry(QtCore.QRect(270, 200, 89, 25))
        self.pushButtonSubmit.setObjectName("pushButtonSubmit")
        self.pushButtonSubmit.setText("Submit")

        self.textEditSystemName = QtWidgets.QTextEdit(Dialog)
        self.textEditSystemName.setGeometry(QtCore.QRect(40, 80, 250, 70))
        self.textEditSystemName.setObjectName("textEditSystemName")

        self.labelSystem=QtWidgets.QLabel(Dialog)
        self.labelSystem.setGeometry(QtCore.QRect(40,40,180,20))
        self.labelSystem.setObjectName("labelSystem")

        if fl==1:
            self.labelSystem.setText("New Bid System Name")
        elif fl==2:
            self.labelSystem.setText("Existing Bid System Name")
        elif fl==3:
            self.labelSystem.setText("New Convention Name")
        elif fl==4:
            self.labelSystem.setText("Existing Convention Name")
        self.lineEditError = QtWidgets.QLineEdit(self.curDialog)
        self.lineEditError.setGeometry(QtCore.QRect(40,200, 190, 25))
        self.lineEditError.setObjectName("lineEditSystemName")
        self.pushButtonSubmit.clicked.connect(self.pushButtonSubmitClicked)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        Dialog.exec()

    def pushButtonSubmitClicked(self):
        currentName=self.textEditSystemName.toPlainText()
        self.currentMenu.systemName=currentName
        df1=DAGFunctions(self.currentMenu.graph)
        
        if self.fl==2 or self.fl==4:
            self.currentMenu.rootNode=df1.findRoot(currentName)
            if self.currentMenu.rootNode==None:
                
                if self.fl==2:
                    self.lineEditError.setText("Bid System does not exist")
                if self.fl==4:
                    self.lineEditError.setText("Convention does not exist")

            else:
                self.curDialog.close()
        else:
            #Need to ensure special characters do not exist!
            self.currentMenu.rootNode=df1.createBiddingSystem(currentName,self.fl)
            if self.currentMenu.rootNode==None:
                if self.fl==1:
                    self.lineEditError.setText("Bid System already exists")
                if self.fl==3:
                    self.lineEditError.setText("Convention already exists")
            else:
                self.curDialog.close()

class OpeningMenu(object):
    def setupUi(self,Dialog,curMenu):
        Dialog.setObjectName("OpeningMenuDialog")
        Dialog.resize(400, 300)
        Dialog.setModal(True)
        Dialog.setWindowTitle("Opening Menu")
        self.currentMenu=curMenu
        self.curDialog=Dialog
        self.pushButtonCreateNewBiddingSystem=QtWidgets.QPushButton(Dialog)
        self.pushButtonCreateNewBiddingSystem.setGeometry(QtCore.QRect(90, 40, 211, 25))
        self.pushButtonCreateNewBiddingSystem.setObjectName("pushButtonCreateNewBiddingSystem")
        self.pushButtonCreateNewBiddingSystem.setText("Create New Bidding System")

        self.pushButtonLoadExistingBiddingSystem=QtWidgets.QPushButton(Dialog)
        self.pushButtonLoadExistingBiddingSystem.setGeometry(QtCore.QRect(90, 80, 211, 25))
        self.pushButtonLoadExistingBiddingSystem.setObjectName("pushButtonLoadExistingBiddingSystem")
        self.pushButtonLoadExistingBiddingSystem.setText("Load Existing Bidding System")

        self.pushButtonCreateNewConvention=QtWidgets.QPushButton(Dialog)
        self.pushButtonCreateNewConvention.setGeometry(QtCore.QRect(90, 120, 211, 25))
        self.pushButtonCreateNewConvention.setObjectName("pushButtonCreateNewConvention")
        self.pushButtonCreateNewConvention.setText("Create New Convention")

        self.pushButtonLoadExistingConvention=QtWidgets.QPushButton(Dialog)
        self.pushButtonLoadExistingConvention.setGeometry(QtCore.QRect(90, 160, 211, 25))
        self.pushButtonLoadExistingConvention.setObjectName("pushButtonLoadExistingConvention")
        self.pushButtonLoadExistingConvention.setText("Load Existing Convention")

        self.pushButtonCreateNewConvention.clicked.connect(self.pushButtonCreateNewConventionClicked)
        self.pushButtonCreateNewBiddingSystem.clicked.connect(self.pushButtonCreateNewBiddingSystemClicked)
        self.pushButtonLoadExistingConvention.clicked.connect(self.pushButtonLoadExistingConventionClicked)
        self.pushButtonLoadExistingBiddingSystem.clicked.connect(self.pushButtonLoadExistingBiddingSystemClicked)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

        Dialog.exec()

    def pushButtonCreateNewBiddingSystemClicked(self):
        Dialog = QtWidgets.QDialog()
        self.currentMenu.systemType="BidSystem"
        ui = ChooseSystem()
        ui.setupUi(Dialog,self.currentMenu,1)
        self.curDialog.close()

    def pushButtonLoadExistingBiddingSystemClicked(self):
        Dialog = QtWidgets.QDialog()
        self.currentMenu.systemType="BidSystem"
        ui = ChooseSystem()
        ui.setupUi(Dialog,self.currentMenu,2)
        self.curDialog.close()

    def pushButtonCreateNewConventionClicked(self):
        Dialog = QtWidgets.QDialog()
        self.currentMenu.systemType="Convention"
        ui = ChooseSystem()
        ui.setupUi(Dialog,self.currentMenu,3)
        self.curDialog.close()

    def pushButtonLoadExistingConventionClicked(self):
        Dialog = QtWidgets.QDialog()
        self.currentMenu.systemType="Convention"
        ui = ChooseSystem()
        ui.setupUi(Dialog,self.currentMenu,4)
        self.curDialog.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow,curMenu,convList,convBidList):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.currentMenu=curMenu
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textEditCurrentChildren = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditCurrentChildren.setGeometry(QtCore.QRect(50, 200, 271, 60))
        self.textEditCurrentChildren.setObjectName("textEditCurrentChildren")
        self.textEditCurrentChildren.setReadOnly(True)
        self.textEditCurrentSequence = QtWidgets.QTextEdit(self.centralwidget)
        self.textEditCurrentSequence.setGeometry(QtCore.QRect(50, 30, 261, 131))
        self.textEditCurrentSequence.setObjectName("textEditCurrentSequence")
        self.textEditCurrentSequence.setReadOnly(True)
        self.pushButtonAddChild = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAddChild.setGeometry(QtCore.QRect(350, 50, 89, 25))
        self.pushButtonAddChild.setObjectName("pushButtonAddChild")
        self.pushButtonAddConvention = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAddConvention.setGeometry(QtCore.QRect(630, 90, 130, 25))
        self.pushButtonAddConvention.setObjectName("pushButtonAddConvention")
        self.pushButtonAddConventionWithOpPass = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAddConventionWithOpPass.setGeometry(QtCore.QRect(630, 130, 130, 50))
        self.pushButtonAddConventionWithOpPass.setObjectName("pushButtonAddConventionWithOpPass")
        # self.pushButtonAddConventionWithOpPass.setWordWrap(True)
        # self.pushButtonDeleteConvention = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButtonDeleteConvention.setGeometry(QtCore.QRect(630, 200, 130, 25))
        # self.pushButtonDeleteConvention.setObjectName("pushButtonDeleteConvention")
        self.pushButtonGetInfo = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonGetInfo.setGeometry(QtCore.QRect(500, 50, 89, 25))
        self.pushButtonGetInfo.setObjectName("pushButtonGetInfo")
        self.pushButtonModifyInfo = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonModifyInfo.setGeometry(QtCore.QRect(500, 90, 89, 25))
        self.pushButtonModifyInfo.setObjectName("pushButtonModifyInfo")
        self.pushButtonAddSubtree = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonAddSubtree.setGeometry(QtCore.QRect(500, 130, 89, 25))
        self.pushButtonAddSubtree.setObjectName("pushButtonAddSubtree")
        self.pushButtonOpPass = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonOpPass.setGeometry(QtCore.QRect(350, 90, 89, 25))
        self.pushButtonOpPass.setObjectName("pushButtonOpPass")
        self.pushButtonChildInfo = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonChildInfo.setGeometry(QtCore.QRect(230, 340, 89, 25))
        self.pushButtonChildInfo.setObjectName("pushButtonChildInfo")
        self.pushButtonGoToRoot = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonGoToRoot.setGeometry(QtCore.QRect(350, 130, 89, 25))
        self.pushButtonGoToRoot.setObjectName("pushButtonGoToRoot")
        self.pushButtonDeleteChild = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonDeleteChild.setGeometry(QtCore.QRect(120, 340, 91, 25))
        self.pushButtonDeleteChild.setObjectName("pushButtonDeleteChild")
        self.pushButtonGoToNode = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonGoToNode.setGeometry(QtCore.QRect(630, 50, 89, 25))
        self.pushButtonGoToNode.setObjectName("pushButtonGoToNode")
        self.pushButtonGoToChild = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonGoToChild.setGeometry(QtCore.QRect(10, 340, 89, 25))
        self.pushButtonGoToChild.setObjectName("pushButtonGoToChild")
        self.comboBoxSelectChild=QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxSelectChild.setGeometry(QtCore.QRect(170,290,86,25))
        self.comboBoxSelectChild.setObjectName("comboBoxSelectChild")
        self.labelSelectChild=QtWidgets.QLabel(self.centralwidget)
        self.labelSelectChild.setGeometry(QtCore.QRect(50,290,86,25))
        self.labelSelectChild.setObjectName("labelSelectChild")

        self.labelCurrentSequence=QtWidgets.QLabel(self.centralwidget)
        self.labelCurrentSequence.setGeometry(QtCore.QRect(50,10,150,25))
        self.labelCurrentSequence.setObjectName("labelCurrentSequence")
        self.labelCurrentSequence.setText("Current Sequence")

        self.labelCurrentChildren=QtWidgets.QLabel(self.centralwidget)
        self.labelCurrentChildren.setGeometry(QtCore.QRect(50,180,150,25))
        self.labelCurrentChildren.setObjectName("labelCurrentChildren")
        self.labelCurrentChildren.setText("Current Children")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.pushButtonAddChild.clicked.connect(self.pushButtonAddChildClicked)
        self.pushButtonOpPass.clicked.connect(self.pushButtonOpPassClicked)
        self.pushButtonGoToRoot.clicked.connect(self.pushButtonGoToRootClicked)
        self.pushButtonGoToNode.clicked.connect(self.pushButtonGoToNodeClicked)
        self.pushButtonGoToChild.clicked.connect(self.pushButtonGoToChildClicked)
        self.pushButtonDeleteChild.clicked.connect(self.pushButtonDeleteChildClicked)
        self.pushButtonChildInfo.clicked.connect(self.pushButtonChildInfoClicked)
        self.pushButtonGetInfo.clicked.connect(self.pushButtonGetInfoClicked)
        self.pushButtonModifyInfo.clicked.connect(self.pushButtonModifyInfoClicked)
        self.pushButtonAddSubtree.clicked.connect(self.pushButtonAddSubtreeClicked)
        self.pushButtonAddConvention.clicked.connect(self.pushButtonAddConventionClicked)
        self.pushButtonAddConventionWithOpPass.clicked.connect(self.pushButtonAddConventionWithOpPassClicked)
        # self.pushButtonDeleteConvention.clicked.connect(self.pushButtonDeleteConventionClicked)

        
        self.currentState=CurrentState(self.currentMenu.systemName,self.currentMenu.graph,self,convList,convBidList)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        
    def pushButtonAddChildClicked(self):
        # Add child function needs to be executed and the 
        # current children at this node needs to get updated.
        Dialog = QtWidgets.QDialog()
        ui = BidDialog()
        ui.setupUi(Dialog,self.currentState,self,1)
        # obj=DAGFunctions(self.currentState.graph)
        # bsname=self.currentState.bidSystemName
        # obj.insertChild(bsname,BidNode(),self.currentState.currentNode,"2C")
        # nodeList=obj.getChildren(bsname,self.currentState.currentNode)
        # bidList=list(map(lambda x : x['bid'], nodeList))
        # my_string = ','.join(map(str, bidList))
        # self.textEdit1.setPlainText(my_string)

    def pushButtonGetInfoClicked(self):
        curNode=self.currentState.currentNode
        # print("Prob ",curNode['HcpUb'])
        Dialog = QtWidgets.QDialog()
        ui = UiDialogBidInfo()
        ui.setupUi(Dialog,self.currentState,self,curNode['bid'],4,curNode,False)

    def pushButtonModifyInfoClicked(self):
        curNode=self.currentState.currentNode
        Dialog = QtWidgets.QDialog()
        ui = UiDialogBidInfo()
        ui.setupUi(Dialog,self.currentState,self,curNode['bid'],3,curNode,True)

    def pushButtonAddConventionClicked(self):
        Dialog = QtWidgets.QDialog()
        ui = UiDialogAddConvention()
        ui.setupUi(Dialog,self.currentState,True)

    def pushButtonAddConventionWithOpPassClicked(self):
        Dialog = QtWidgets.QDialog()
        ui = UiDialogAddConvention()
        ui.setupUi(Dialog,self.currentState,False)

    # def pushButtonDeleteConventionClicked(self):
    #     Dialog=QtWidgets.QDialog()
    #     ui=UiDialogDeleteConvention()
    #     ui.setupUi(Dialog,self.currentState) 
    
    def showWarningDeleteChild(self):
        msgDeleteChild=QtWidgets.QMessageBox()
        msgDeleteChild.setWindowTitle("Warning!")
        msgDeleteChild.setText("Deletion of child will delete entire subgraph rooted at the child Node! Do u want to Go Ahead?")
        msgDeleteChild.setIcon(QtWidgets.QMessageBox.Warning)
        msgDeleteChild.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        msgDeleteChild.buttonClicked.connect(self.popup_button)
        msgDeleteChild.exec()


    def popup_button(self,pressedButton):
        # print(pressedButton.text())
        # print(pressedButton)
        if pressedButton.text()=="&Yes":
            # print("FOFF")
            df=DAGFunctions(self.currentState.graph)
            cbid=df.bidToInt[self.childToBeDeleted['bid']]
            self.currentState.currentNode['AllowedBids'][cbid]=True
            df.graph.push(self.currentState.currentNode)
            df.deleteChildRec(self.currentState.bidSystemName,
                    self.childToBeDeleted)
            modList=df.getChildren(self.currentState.bidSystemName,self.currentState.currentNode)
            self.currentState.updateChildren(modList)

    def pushButtonDeleteChildClicked(self):
        curChild=self.comboBoxSelectChild.currentText()
        df=DAGFunctions(self.currentState.graph)
        cNode=None
        if(curChild!="None"):
            for j in range(len(self.currentState.currentChildren)):
                if self.currentState.currentChildren[j]['bid']==curChild:
                    cNode=self.currentState.currentChildren[j]                    
                    break
            
            if cNode!=None:
                bval=df.deleteChild(self.currentState.bidSystemName,
                    self.currentState.currentNode,cNode)
                if bval==True:
                    modList=df.getChildren(self.currentState.bidSystemName,self.currentState.currentNode)
                    self.currentState.updateChildren(modList)
                else:
                    self.childToBeDeleted=cNode
                    self.showWarningDeleteChild()

    def pushButtonOpPassClicked(self):
        Dialog = QtWidgets.QDialog()
        ui = BidDialog()
        ui.setupUi(Dialog,self.currentState,self,2)

    def pushButtonGoToRootClicked(self):
        self.currentState.updateNode("")
        self.currentState.pathLength=0
        self.currentState.curNodeHandList=[PlayerHand(),PlayerHand(),PlayerHand(),PlayerHand()]
        self.currentState.prevNodeHandList=[PlayerHand(),PlayerHand(),PlayerHand(),PlayerHand()]

    def pushButtonGoToNodeClicked(self):
        Dialog = QtWidgets.QDialog()
        ui = GoToNodeDialog()
        ui.setupUi(Dialog,self.currentState,self,1)

    def pushButtonAddSubtreeClicked(self):
        Dialog = QtWidgets.QDialog()
        ui = GoToNodeDialog()
        ui.setupUi(Dialog,self.currentState,self,2)        

    def pushButtonGoToChildClicked(self):
        curChild=self.comboBoxSelectChild.currentText()
        df=DAGFunctions(self.currentState.graph)
        if(curChild!="None"):
            for j in range(len(self.currentState.currentChildren)):
                if self.currentState.currentChildren[j]['bid']==curChild:
                    self.currentState.currentNode=self.currentState.currentChildren[j]
                    newChildren=df.getChildren(self.currentState.bidSystemName,self.currentState.currentNode)
                    if self.currentState.curSeq=="":
                        self.currentState.curSeq=curChild
                    else:
                        self.currentState.curSeq=self.currentState.curSeq+"-"+curChild
                    self.textEditCurrentSequence.setPlainText(self.currentState.curSeq)
                    self.currentState.updateChildren(newChildren)
                    self.currentState.pathLength+=1
                    curHand=df.getHandInfo(self.currentState.currentNode)
                    prevList=self.currentState.curNodeHandList
                    newList=copy.deepcopy(self.currentState.curNodeHandList)
                    newList[(self.currentState.pathLength-1)%4]=curHand
                    finList=df.constraintPropagation(prevList,newList)
                    self.currentState.curNodeHandList=finList[0]
                    self.currentState.prevNodeHandList=newList
                    break

    def pushButtonChildInfoClicked(self):
        curChild=self.comboBoxSelectChild.currentText()
        df=DAGFunctions(self.currentState.graph)
        cNode=None
        if(curChild!="None"):
            for j in range(len(self.currentState.currentChildren)):
                if self.currentState.currentChildren[j]['bid']==curChild:
                    cNode=self.currentState.currentChildren[j]
                    break
            if cNode!=None:
                Dialog = QtWidgets.QDialog()
                ui = UiDialogBidInfo()
                ui.setupUi(Dialog,self.currentState,self,cNode['bid'],4,cNode,False)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButtonAddChild.setText(_translate("MainWindow", "AddChild"))
        self.pushButtonAddChild.adjustSize()
        self.pushButtonOpPass.setText(_translate("MainWindow", "AddChildWithOpPass"))
        self.pushButtonOpPass.adjustSize()
        self.pushButtonGoToRoot.setText(_translate("MainWindow", "GoToRoot"))
        self.pushButtonGoToRoot.adjustSize()
        self.pushButtonGoToNode.setText(_translate("MainWindow", "GoToNode"))
        self.pushButtonGoToNode.adjustSize()
        self.pushButtonGoToChild.setText(_translate("MainWindow", "GoToChild"))
        self.pushButtonGoToChild.adjustSize()
        self.labelSelectChild.setText(_translate("Dialog", "Select Child"))
        self.pushButtonDeleteChild.setText(_translate("Dialog", "Delete Child"))
        self.pushButtonGetInfo.setText(_translate("Dialog","Get Info"))
        self.pushButtonModifyInfo.setText(_translate("Dialog","Modify Info"))
        self.pushButtonChildInfo.setText(_translate("Dialog","Child Info"))
        self.pushButtonAddSubtree.setText(_translate("Dialog","Add Subtree"))
        self.pushButtonAddConvention.setText(_translate("Dialog","Add Convention"))
        # self.pushButtonDeleteConvention.setText(_translate("Dialog","Delete Convention"))
        self.pushButtonAddConventionWithOpPass.setText(_translate("Dialog","Add Convention \n With Op Pass"))
        # self.pushButtonDeleteConvention.setText(_translate("Dialog","Delete Convention"))

if __name__ == "__main__":
    import sys
    from py2neo import Graph
    from py2neo import Node
    from py2neo import Relationship
    from py2neo import *
    graph = Graph("neo4j://localhost:7687", auth=("neo4j", "laasyaugrc"))
    # graph.delete_all()
    # df1=DAGFunctions(graph)
    # rootNode=df1.createBiddingSystem("BergenRaiseSpade")
    # r1=df1.createBiddingSystem("Jacoby2NTSpade")
    # r11=df1.insertChild("Jacoby2NTSpade",BidNode(),r1,"2NT")
    # r2=df1.createBiddingSystem("SplinterSpade")
    # r21=df1.insertChild("SplinterSpade",BidNode(),r2,"4C")
    # r22=df1.insertChild("SplinterSpade",BidNode(),r2,"4D")
    # r23=df1.insertChild("SplinterSpade",BidNode(),r2,"4H")
    # r3=df1.createBiddingSystem("SelfSplinterSpade")
    # rootNode=df1.findRoot("Jacoby2NTSpade")
    app = QtWidgets.QApplication(sys.argv)

    currentMenu=CurrentMenu(graph)
    Dialog=QtWidgets.QDialog()
    ui1=OpeningMenu()
    ui1.setupUi(Dialog,currentMenu)

    if currentMenu.rootNode==None:
        # sys.exit(app.exec_())
        app.exit()
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    conventionList=["Jacoby2NTSpade","SplinterSpade","SelfSplinterSpade","Stayman","BergenRaiseSpade"]
    conventionBidDict={"Jacoby2NTSpade":["2NT"],"SplinterSpade":["4C","4D","4H"],
    "SelfSplinterSpade":["4C","4D","4H"],"Stayman":["2C"],"BergenRaiseSpade":["3C","3D","3H","3S"]}
    ui.setupUi(MainWindow,currentMenu,conventionList,conventionBidDict)
    MainWindow.show()
    sys.exit(app.exec_())
