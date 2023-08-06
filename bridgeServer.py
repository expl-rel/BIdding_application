from operator import truediv
import os, socket
from _thread import *
import threading
import json
from py2neo import *
import sys
import itertools,random
import numpy as np


class PlayerCards:
    def __init__(self):
        self.spadeCards=[]
        self.heartCards=[]
        self.diamondCards=[]
        self.clubCards=[]
        self.longestSuit=None

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


class PlayerHand:
    def __init__(self):
        self.hcpBounds=[0,37]
        # self.totalPoints=[0,40]
        #Cards of holder in order of suits S,H,D,C
        self.suits=[SuitCards(),SuitCards(),SuitCards(),SuitCards()]

        # S,H,D,C or None
        self.longestSuit=None
        
    def __eq__(self, other):
        
        if not isinstance(other, PlayerHand):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.hcpBounds == other.hcpBounds and 
         self.suits == other.suits and self.longestSuit==other.longestSuit)


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
        self.forcing=False
        self.isParentForcing=False
        self.allowedBids=[True]*38
        #self.opening=False
        self.hand=PlayerHand()
       
        #Like opening, response, overcall, asking, respondingToAsk
        self.biddingCategory=BidCategory()
        
        #Like pre emptive or support or cue
        self.biddingDescription=BidDescription()



class BidEmulator:
    def __init__(self):
        # These values are updated after the algo to check input constraints is satisfied
        self.actualCards=[PlayerCards(),PlayerCards(),PlayerCards(),PlayerCards()]
        self.hands=[PlayerHand(),PlayerHand(),PlayerHand(),PlayerHand()]
        self.constraintHands=[[self.hands[0],PlayerHand(),PlayerHand(),PlayerHand()]
        ,[PlayerHand(),self.hands[1],PlayerHand(),PlayerHand()]
        ,[PlayerHand(),PlayerHand(),self.hands[2],PlayerHand()]
        ,[PlayerHand(),PlayerHand(),PlayerHand(),self.hands[3]]]
        self.df=None
        self.graphName=None
        self.bidSystem=None
        self.n_iter=10000000
        self.bids= ["1C","1D","1H","1S","1NT",
                    "2C","2D","2H","2S","2NT",
                    "3C","3D","3H","3S","3NT",
                    "4C","4D","4H","4S","4NT",
                    "5C","5D","5H","5S","5NT",
                    "6C","6D","6H","6S","6NT",
                    "7C","7D","7H","7S","7NT",
                    "P","dbl","redbl"]
        self.constrained=[PlayerHand(),PlayerHand(),PlayerHand(),PlayerHand(),[0,40],[0,40]]
        self.bidSeq=""

    def initBidSystem(self,bidSystem,userId,pwd):
        self.graphName=Graph(auth=(userId,pwd))
        from df import DAGFunctions
        self.df=DAGFunctions(self.graphName)
        self.bidSystem=bidSystem

    # The end marker used for all the data is $$
    def recvall(self,the_socket):
        End='$$'
        total_data=[]
        data=''
        while True:
            data=the_socket.recv(8192)
            if not data:
                print("\nconnection with client broken\n")
                the_socket.close()
                sys.exit()
                break
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
        return ''.join(total_data)




    """
    Input dictionary valid syntax

    S.No.   Key                     Value

    1.      Opening                 Any bid value(1S to 7NT)
                                    However you need to ensure that this opening bid exists in your bidding DAG


    2.      North                   Hand-Dictionary

    3.      East                    Hand-Dictionary

    4.      South                   Hand-Dictionary

    5.      West                    Hand-Dictionary

    6.      North-South-total-hcp   Numbers(Lb and Ub in a list) between 0-40 . Ex:[10,25]

    7.      East-West-total-hcp     Numbers between 0-40


    Hand-Dictionary valid syntax

    S.No.   Key                     Value

    1.      SpadeLength             Numbers 0-13

    2.      SpadeHCP                Numbers 0-10

    3.      HeartLength             Numbers 0-13

    4.      HeartHCP                Numbers 0-10

    5.      DiamondLength           Numbers 0-13

    6.      DiamondHCP              Number 0-10

    7.      ClubLength              Number 0-13

    8.      ClubHCP                 Number 0-10

    9.      TotalHCP                Number 0-37


    """
    
    def handle_client2(self,roomId):
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # bind the socket to a public host, and a well-known port
        try:
            # s.bind((socket.gethostname(), roomId))
            s.bind("127.0.0.1",roomId)
            print("socket binded to port")
        
        except socket.error as e:
            print(str(e))


        # allow port forwarding through the router to your machine
        
        # Max number of connections that can be waiting
        s.listen(1)
        (clientsocket, address) = s.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        s.close()
        return clientsocket

    def nodeToHand(self,n):
        c=PlayerHand()
        c.longestSuit=n['longestSuit']
        
        c.suits[0].suitLength[0]=n['SuitLengthLb'][0]
        c.suits[1].suitLength[0]=n['SuitLengthLb'][1]
        c.suits[2].suitLength[0]=n['SuitLengthLb'][2]
        c.suits[3].suitLength[0]=n['SuitLengthLb'][3]

        c.suits[0].suitLength[1]=n['SuitLengthUb'][0]
        c.suits[1].suitLength[1]=n['SuitLengthUb'][1]
        c.suits[2].suitLength[1]=n['SuitLengthUb'][2]
        c.suits[3].suitLength[1]=n['SuitLengthUb'][3]

        c.suits[0].suitHcp[0]=n['SuitHcpLb'][0]
        c.suits[1].suitHcp[0]=n['SuitHcpLb'][1]
        c.suits[2].suitHcp[0]=n['SuitHcpLb'][2]
        c.suits[3].suitHcp[0]=n['SuitHcpLb'][3]

        c.suits[0].suitHcp[1]=n['SuitHcpUb'][0]
        c.suits[1].suitHcp[1]=n['SuitHcpUb'][1]
        c.suits[2].suitHcp[1]=n['SuitHcpUb'][2]
        c.suits[3].suitHcp[1]=n['SuitHcpUb'][3]

        c.hcpBounds[0]=n['HcpLb']
        c.hcpBounds[1]=n['HcpUb']

        for i in range(4):
            c.suits[i].cards=n['SuitCards'][i*13:i*13+13]
        return c
    
    def updateConst(c1,c2):
        errMsg=None
        bval=True
        c=PlayerHand()
        if not c1.longestSuit==c2.longestSuit:
            if c1.longestSuit==None:
                c.longestSuit=c2.longestSuit
            elif c2.longestSuit==None:
                c.longestSuit=c1.longestSuit
            else:
                bval=False
                errMsg="Multiple Longest suits specified for same hand"
                return [bval,errMsg,c]
        else:
            c.longestSuit=c1.longestSuit
        
        for i in range(4):
            c.suits[i].suitLength[0]=max(c1.suits[i].suitLength[0],c2.suits[i].suitLength[0])
            c.suits[i].suitLength[1]=min(c1.suits[i].suitLength[1],c2.suits[i].suitLength[1])

            c.suits[i].suitHcp[0]=max(c1.suits[i].suitHcp[0],c2.suits[i].suitHcp[0])
            c.suits[i].suitHcp[1]=min(c1.suits[i].suitHcp[1],c2.suits[i].suitHcp[1])
            
            for j in range(13):
                if not c1.suits[i].cards[j]==c2.suits[i].cards[j]:
                    if c1.suits[i].cards[j]==0:
                        c.suits[i].cards[j]=c2.suits[i].cards[j]
                    elif c2.suits[i].cards[j]==0:
                        c.suits[i].cards[j]=c1.suits[i].cards[j]
                    else:
                        bval=False
                        errMsg="Opposing cards yes or no specified for same hand"
                        return [bval,errMsg,c]
        
        c.hcpBounds[0]=max(c1.hcpBounds[0],c2.hcpBounds[0])
        c.hcpBounds[1]=min(c1.hcpBounds[1],c2.hcpBounds[1])

        return [bval,errMsg,c]
            
    def handle_inpConstraints(self,inpDic):
        errMsg=None
        bval=True
        for key in inpDic:
            val=inpDic[key]
            if key=="Opening":
                if val not in self.bids:
                    bval=False
                    print("Bid value sent is not valid")
                    errMsg="Bid is not valid"
                    return [False,errMsg]
                else:
                    nodeFound=self.df.findNode(self.bidSystem,val)
                    if nodeFound==None:
                        bval=False
                        print("Bid value is not an opening bid in used bidding system")
                        errMsg="Bid is not an opening bid in used bidding system"
                        return [False,errMsg]
                    else:
                        # First player hand
                        nHand=self.nodeToHand(nodeFound)
                        lis=self.updateConst(nHand,self.constrained[0])
                        if lis[0]==False:
                            print(lis[1])
                            return [False,lis[1]]
                        else:
                            self.constrained[0]=lis[2]
            
            elif key=="North-South-total-hcp":
                self.constrained[4]=val

            elif key=="East-West-total-hcp":
                self.constrained[5]=val
            
            elif key=="North" or key=="East" or key=="South" or key=="West":
                ind=-1
                if key=="North":
                    ind=0
                elif key=="East":
                    ind=1
                elif key=="South":
                    ind=2
                else:
                    ind=3
                
                c1=PlayerHand()
                for k in val:

                    if k=="SpadeLength":
                        c1.suits[0].suitLength=val[k]
                    elif k=="SpadeHcp":
                        c1.suits[0].suitHcp=val[k]

                    elif k=="HeartLength":
                        c1.suits[1].suitLength=val[k]
                    elif k=="HeartHcp":
                        c1.suits[1].suitHcp=val[k]

                    elif k=="DiamondLength":
                        c1.suits[2].suitLength=val[k]
                    elif k=="DiamondHcp":
                        c1.suits[2].suitHcp=val[k]
                    
                    elif k=="ClubLength":
                        c1.suits[3].suitLength=val[k]
                    elif k=="ClubHcp":
                        c1.suits[3].suitHcp=val[k]
                    
                    elif k=="TotalHcp":
                        c1.hcpBounds=val[k]
                    
                    else:
                        errMsg="Wrong key specified: "+k+" in hand dictionary for hand: "+ key
                        return [False,errMsg]
                
                lis=self.updateConst(c1,self.constrained[ind])
                if lis[0]==False:
                    print(lis[1])
                    return [False,lis[1]]
                else:
                    self.constrained[ind]=lis[2]
        bval=self.createHands()
        return [bval,errMsg]
    
    def generateHands(self):
        # make a deck of cards
        deck = list(itertools.product(range(2,15),['S','H','D','C']))

        # shuffle the cards
        random.shuffle(deck)

        return deck

    def checkConstraint(self,cards):
        nsHcp=0
        ewHcp=0
        for i in range(4):
            
            totHcp=sum(filter(lambda x: x[0]>=10, cards[i*13:i*13+13]))
            if i==0 or i==2:
                nsHcp+=totHcp
            else:
                ewHcp+=totHcp
            spadeList=filter(lambda x:x[1]=="S", cards[i*13:i*13+13])
            spadeHcp=sum(filter(lambda x: x[0]>=10,spadeList))
            heartList=filter(lambda x:x[1]=="H", cards[i*13:i*13+13])
            heartHcp=sum(filter(lambda x: x[0]>=10,heartList))
            diamondList=filter(lambda x:x[1]=="D", cards[i*13:i*13+13])
            diamondHcp=sum(filter(lambda x: x[0]>=10,diamondList))
            clubList=filter(lambda x:x[1]=="C", cards[i*13:i*13+13])
            clubHcp=sum(filter(lambda x: x[0]>=10,clubList))
            suitList=[spadeList,heartList,diamondList,clubList]
            hcpList=[spadeHcp,heartHcp,diamondHcp,clubHcp]
            str1="SHDC"
            if self.constrained[i].longestSuit!=None:
                ind=str1.find(self.constrained[i].longestSuit)
                if ind>=0:
                    val=len(suitList[ind])
                    b1=val>=len(suitList[0]) and val>=len(suitList[1]) and val>=len(suitList[2]) and val>=len(suitList[3])
                    if b1==False:
                        return b1
            bval=True
            b1=self.constrained[i].hcpBounds[0]<=totHcp and totHcp<=self.constrained[i].hcpBounds[1]
            if b1==False:
                return b1
            for j in range(4):
                b1=self.constrained[i].suits[j].suitHcp[0]<=hcpList[j] and hcpList[j]<=self.constrained[i].suits[j].suitHcp[1]           
                if b1==False:
                    return b1
                
                b1=self.constrained[i].suits[j].suitLength[0]<=len(suitList[j]) and len(suitList[j])<=self.constrained[i].suits[j].suitLength[1]        
                if b1==False:
                    return b1
        b1=self.constrained[4][0]<=nsHcp and ncHcp<=self.constrained[4][1] and self.constrained[5][0]<=ewHcp and ewHcp<=self.constrained[5][1]
        if b1==False:
            return b1
        return True

    def cardToHand(self,p):
        str1="JQKA"
        str2="AKQJT98765432"
        h=PlayerHand()
        h.suits[0].cards=[-1]*13
        for i in p.spadeCards:
            ind=str1.find(i)
            if ind>=0:
                h.suits[0].suitHcp[0]+=ind+1
            ind1=str2.find(i)
            if ind1>=0:
                h.suits[0].cards[ind1]=1
        h.suits[0].suitLength[0]=len(p.spadeCards)
        h.suits[0].suitLength[1]=len(p.spadeCards)
        h.suits[0].suitHcp[1]=h.suits[0].suitHcp[0]

        h.suits[1].cards=[-1]*13
        for i in p.heartCards:
            ind=str1.find(i)
            if ind>=0:
                h.suits[1].suitHcp[0]+=ind+1
            ind1=str2.find(i)
            if ind1>=0:
                h.suits[1].cards[ind1]=1
        h.suits[1].suitLength[0]=len(p.spadeCards)
        h.suits[1].suitLength[1]=len(p.spadeCards)
        h.suits[1].suitHcp[1]=h.suits[0].suitHcp[0]

        h.suits[2].cards=[-1]*13
        for i in p.diamondCards:
            ind=str1.find(i)
            if ind>=0:
                h.suits[2].suitHcp[0]+=ind+1
            ind1=str2.find(i)
            if ind1>=0:
                h.suits[2].cards[ind1]=1
        h.suits[2].suitLength[0]=len(p.spadeCards)
        h.suits[2].suitLength[1]=len(p.spadeCards)
        h.suits[2].suitHcp[1]=h.suits[0].suitHcp[0]

        h.suits[3].cards=[-1]*13
        for i in p.clubCards:
            ind=str1.find(i)
            if ind>=0:
                h.suits[3].suitHcp[0]+=ind+1
            ind1=str2.find(i)
            if ind1>=0:
                h.suits[3].cards[ind1]=1
        h.suits[3].suitLength[0]=len(p.spadeCards)
        h.suits[3].suitLength[1]=len(p.spadeCards)
        h.suits[3].suitHcp[1]=h.suits[0].suitHcp[0]



        h.hcpBounds[0]=h.suits[0].suitHcp[0]+h.suits[1].suitHcp[0]+h.suits[2].suitHcp[0]+h.suits[3].suitHcp[0]
        h.hcpBounds[1]=h.hcpBounds[0]
        h.longestSuit=p.longestSuit
        return h

    def cardCreator(self,cards):
        str1="xx23456789TJQKA"
        p1=PlayerCards()
        spadeList=filter(lambda x:x[1]=="S",cards)
        p1.spadeCards=map(lambda x:str1[x[0]],spadeList)
        heartList=filter(lambda x:x[1]=="H",cards)
        p1.heartCards=map(lambda x:str1[x[0]],heartList)
        diamondList=filter(lambda x:x[1]=="D",cards)
        p1.diamondCards=map(lambda x:str1[x[0]],diamondList)
        clubList=filter(lambda x:x[1]=="C",cards)
        p1.clubCards=map(lambda x:str1[x[0]],clubList)
        return p1


        

    def createHands(self):
        for i in range(self.n_iter):
            cards=self.generateHands()
            bval=self.checkConstraint(cards)
            if bval==True:
                for i in range(4):
                    self.actualCards[i]=self.cardCreator(cards[i*13:i*13+13])
                    self.actualCards[i].longestSuit=self.constrained[i].longestSuit
                    self.hands[i]=self.cardToHand(self.actualCards[i])
                    self.constraintHands[i]=self.df.constraintPropagation([PlayerHand()]*4,self.constraintHands[i])[0]
                return True
        return False

    def createAllpDict(self,l,p,ind):
        dic1={}
        dic1['North']=self.create1pDict(l[0])
        dic1['East']=self.create1pDict(l[1])
        dic1['South']=self.create1pDict(l[2])
        dic1['West']=self.create1pDict(l[3])
        dic1['cards']=[p.spadeCards,p.heartCards,p.diamondCards,p.clubCards]
        dic1['bidSequence']=self.bidSeq
        ind1=-1
        if self.bidSeq=="":
            ind1=0
        else:
            l1=self.bidSeq.split('-')
            ind1=len(l1)%4
        lof=["North","East","South","West"]
        
        dic1["Turn"]=lof[ind1]
        return dic1

    def create1pDict(self,p1):
        cardDic1={}
        cardDic1['totalHCPLB']=p1.hcpBounds[0]
        cardDic1['totalHCPUB']=p1.hcpBounds[1]
        # cardDic1['clubHCP']=p1.suits[3].suitHcp
        # cardDic1['diamondHCP']=p1.suits[2].suitHcp
        # cardDic1['heartHCP']=p1.suits[1].suitHcp
        # cardDic1['spadeHCP']=p1.suits[0].suitHcp
        # cardDic1['clubLen']=p1.suits[3].suitLength
        # cardDic1['diamondLen']=p1.suits[2].suitLength
        # cardDic1['heartLen']=p1.suits[1].suitLength
        # cardDic1['spadeLen']=p1.suits[0].suitLength
        # cardDic1['clubCards']=p1.suits[3].cards
        # cardDic1['diamondCards']=p1.suits[2].cards
        # cardDic1['heartCards']=p1.suits[1].cards
        # cardDic1['spadeCards']=p1.suits[0].cards
        cardDic1['suitHcpLB']=[p1.suits[0].suitHcp[0],p1.suits[1].suitHcp[0],p1.suits[2].suitHcp[0],p1.suits[3].suitHcp[0]]
        cardDic1['suitHcpUB']=[p1.suits[0].suitHcp[1],p1.suits[1].suitHcp[1],p1.suits[2].suitHcp[1],p1.suits[3].suitHcp[1]]
        cardDic1['suitLengthLB']=[p1.suits[0].suitLength[0],p1.suits[1].suitLength[0],p1.suits[2].suitLength[0],p1.suits[3].suitLength[0]]
        cardDic1['suitLengthUB']=[p1.suits[0].suitLength[1],p1.suits[1].suitLength[1],p1.suits[2].suitLength[1],p1.suits[3].suitLength[1]]
        cardDic1['longestSuit']=p1.longestSuit
        cardDic1['cards']=[p1.suits[0].cards,p1.suits[1].cards,p1.suits[2].cards,p1.suits[3].cards]
        return cardDic1

    def checkBid(self,h,ah):
        errMsg=None
        slen=[]
        mlen=-1
        sl=["Spade","Heart","Diamond","Club"]
        for i in range(4):
            slen.append(len(filter(lambda x:x==1,ah.suits[i].cards)))
            if ah.suits[i].suitHcp[0]<h.suits[i].suitHcp[0] or ah.suits[i].suitHcp[0]>h.suits[i].suitHcp[1]:
                errMsg="SuitHcp out of bounds for suit "+sl[i]
                return [False,errMsg,h]
            if ah.suits[i].suitLength[0]<h.suits[i].suitLength[0] or ah.suits[i].suitLength[0]>h.suits[i].suitLength[1]:
                errMsg="SuitLength out of bounds for suit "+sl[i]
                return [False,errMsg,h]
        if ah.hcpBounds[0]<h.hcpBounds[0] or ah.hcpBounds[0]>h.hcpBounds[1]:
            errMsg="TotalHcp out of bounds"
            return [False,errMsg,h]
        if h.longestSuit!=None:
            for i in range(4):
                mlen=max(slen[i],mlen)
            str1="SHDC"
            ind1=str1.find(h.longestSuit)
            if ind1==-1:
                print("Error only allowed values are S,H,D,C")
                return [False,"Longest suit value is not among S,H,D,C",h]
            else:
                if slen[ind1]!=mlen:
                    return [False,"Longets suit indicated by bid is not the longest suit",h]
        return [True,errMsg,h]

    def bidEmUpdate(self,hval,ind,bidVal):
        lis=self.checkBid(hval,self.hands[ind])
        if lis[0]==False:
            return lis
        else:
            nformLis=[]
            for i in range(4):
                newLis=[self.constraintHands[i][0],self.constraintHands[i][1],self.constraintHands[i][2],self.constraintHands[i][3]]
                newLis[ind]=hval
                lis=self.df.constraintPropagation(self.constraintHands[i],newLis)
                if lis[1]!=None:
                    return [False,"In constraint propagation: "+lis[1],hval]
                nformLis.append(lis[0])
            self.constraintHands=nformLis
            if self.bidSeq=="":
                self.bidSeq+=bidVal
            else:
                self.bidSeq+="-"+bidVal
            return [True,None,hval]

    def handle_bids(self,bidVal,ind):
        errMsg=None
        curKey=self.bidSeq
        if curKey=="":
            curKey+=bidVal
        else:
            curKey+="-"+bidVal
        ptrNode=self.df.findNode(self.bidSystem,curKey)
        if ptrNode==None:
            errMsg="bid is not a child in bidding DAG"
            return [False,errMsg,PlayerHand()]
        else:
            hval=self.nodeToHand(ptrNode)
            return self.bidEmUpdate(hval,ind,bidVal)
            
    


    def handle_clients(self,s):
        
        # After client 1 connects to server the server sends connection successful msg to client
        data="Connection successful"
        data+="$$"
        s.sendall(bytes(data,encoding="utf-8"))

        # Server receives input constraints from client as long as a satisfiable constraint is obtained
        # Server sends a msg if the constraints are satisfied or not
        bval=False
        while(not bval):
            # Receive input constraints from the client
            received = self.recvall(s)
            received = received.decode("utf-8")
            inpConstraintsDict=json.loads(received)
            # Check if the input constraints can be satisfied and fill the cards of the players
            # Also fill the hands of the players and initialise the constraint prop data.
            bval=self.handle_inpConstraints(inpConstraintsDict)
            m = {"satisfied": bval} 
            data = json.dumps(m)
            # Add the end marker
            data+="$$"
            s.sendall(bytes(data,encoding="utf-8"))


        # Client says ok just to ensure that there is gap between communication
        rec=self.receiveall(s)

        # Server sends the client the threadId which is also the port number to which the client2 should connect to
        ctid=threading.get_ident()
        m = {"id": int(ctid)}
        data = json.dumps(m)
        # Add the end marker
        data+="$$"
        s.sendall(bytes(data,encoding="utf-8"))
        
        # Receive just ok from both clients to prevent loss of data in buffer
        rec1=self.receiveall(s)
        
        # Server waits for client2 to connect
        s2=self.handle_client2(ctid)
        # After cliennt2 connects server sends connection successful to client2
        data="Connection successful"
        data+="$$"
        s2.sendall(bytes(data,encoding="utf-8"))
        
        

       
#        s.sendall(bytes(data,encoding="utf-8"))
        
        # Receive just ok from both clients to prevent loss of data in buffer
        rec2=self.receiveall(s2)
#        rec1=self.receiveall(s)
        
                

        # Now send the NE combined info to client 1 and SW combined info to client2
        while(True):
            dicN=self.createAllpDict(self.constraintHands[0],self.actualCards[0],0)
            dicE=self.createAllpDict(self.constraintHands[1],self.actualCards[1],1)
            dicS=self.createAllpDict(self.constraintHands[2],self.actualCards[2],2)
            dicW=self.createAllpDict(self.constraintHands[3],self.actualCards[3],3)

            dicC1={}
            dicC2={}

            dicC1['P1View']=dicN
            dicC1['P2View']=dicE
            dicC1['end']=False;
            dicC2['end']=False;
            dicC2['P1View']=dicS
            dicC2['P2View']=dicW

            
            data1=json.dumps(dicC1)
            data2=json.dumps(dicC2)
            data1+="$$"
            data2+="$$"

            # Send the dicts to both the players
            s.sendall(bytes(data1,encoding="utf-8"))
            s2.sendall(bytes(data2,encoding="utf-8"))

            # Accept bid from the player and receive ok message from other player
            ind1=-1
            bidVal=""
            if self.bidSeq=="":
                ind1=0
            else:
                ind1=len(self.bidSeq.split('-'))%4
            bval=False
            if ind1<2:
                okStr=self.recvall(s2)
            else:
                okstr=self.recvall(s)

            csock=s
            if ind1>=2:
                csock=s2
            while bval==False:
                bidVal=self.recvall(csock)
                lval=self.handle_bids(bidVal)
                bval=lval[0]
                if bval==True:
                    di1={}
                    di1['bid']=True
                    data=json.dumps(di1)
                    data+="$$"
                    csock.sendall(bytes(data,encoding="utf-8"))
                    okstr=self.recvall(csock)
                    if self.bidSeq!="":
                        tbl=self.bidSeq.split('-')
                        if len(tbl>=3):
                            if tbl[-1]=="P" and tbl[-2]=="P" and tbl[-3]=="P":
                                de1={}
                                de1['end']=True
                                de1['Northcards']=[self.actualCards[0].spadeCards,self.actualCards[0].heartCards,self.actualCards[0].diamondCards,self.actualCards[0].clubCards]
                                de1['Eastcards']=[self.actualCards[1].spadeCards,self.actualCards[1].heartCards,self.actualCards[1].diamondCards,self.actualCards[1].clubCards]
                                de1['Southcards']=[self.actualCards[2].spadeCards,self.actualCards[2].heartCards,self.actualCards[2].diamondCards,self.actualCards[2].clubCards]
                                de1['Westcards']=[self.actualCards[3].spadeCards,self.actualCards[3].heartCards,self.actualCards[3].diamondCards,self.actualCards[3].clubCards]
                                

                                data=json.dumps(de1)
                                data+="$$"
                                s.sendall(bytes(data,encoding="utf-8"))
                                s2.sendall(bytes(data,encoding="utf-8"))
                                s.close()
                                s2.close()
                                sys.exit()


                else:
                    while(True):
                        di1={}
                        di1['bid']=False
                        di1['errStr']=lval[1]
                        di2=self.create1pDict(lval[2])
                        di1['hand']=di2
                        data=json.dumps(di1)
                        data+="$$"
                        csock.sendall(bytes(data,encoding="utf-8"))
                        drec=self.recvall(csock)
                        dicr=json.loads(drec)
                        if dicr['nodeUpdate']==False:
                            data="ok$$"
                            csock.sendall(bytes(data,encoding="utf-8"))
                            break
                        else:
                            hval=dicr['hand']
                            lval=self.bidEmUpdate(hval,ind1,bidVal)
                            bval=lval[0]
                            if bval==True:
                                # Need to add a function modify node which does this
                                self.df.modifyNode(self.bidSeq,hval)
                                dr1={}
                                dr1['bid']=True
                                data=json.dumps(dr1)
                                data+="$$"
                                csock.sendall(bytes(data,encoding="utf-8"))
                                okstr=self.recvall(csock)
                                break


        def server(self):
            ThreadCount=0
            # create an INET, STREAMing socket
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)


            # bind the socket to a public host, and a well-known port
            try:
                # s.bind((socket.gethostname(), 80))
                s.bind("127.0.0.1",80)
                print("socket binded to port")
            
            except socket.error as e:
                print(str(e))


            # allow port forwarding through the router to your machine
            
            # Max number of connections that can be waiting
            s.listen(5)
            print("socket is listening")
            tdic={}
            while True:
                # accept connections from outside
                (clientsocket, address) = s.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                # Create a thread and let the new thread handle the client
                ctid=start_new_thread(handle_clients, (clientsocket, ))
                tdic[ctid]=clientsocket
                print(type(ctid))
                ThreadCount += 1
                print('Thread Number: ' + str(ThreadCount))
            s.close()


bem=BidEmulator()
bem.initBidSystem("tr4","neo4j","laasyaugrc")
bem.server()

