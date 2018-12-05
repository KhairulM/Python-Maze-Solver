import cv2
import numpy as np
import time
import math

"""
Peraturan gambar Maze-nya :

1. Pintu masuk berada di atas dan cuma satu
2. Pintu keluar berada di bawah dan cuma satu
3. Kotak terluar dari maze hanyalah pintu masuk dan keluar, sisanya dinding hitam atau border
4. Terdapat minimal 1 jalur/lintasan dari pintu masuk sampai pintu keluar (min. 1 solusi)       # Mungkin bisa dimodif lagi nanti

"""

def drawPath(dataNodes, solveStack, mazeImg) :
    lenStack = len(solveStack)
    i = 0

    while(i + 1 < lenStack) :
        currPos = (dataNodes[solveStack[i]][0], dataNodes[solveStack[i]][1])
        nextPos = (dataNodes[solveStack[i + 1]][0], dataNodes[solveStack[i + 1]][1])
        cv2.line(mazeImg, currPos, nextPos, (0, 0, 200), 1)
        i += 1

def drawGraph(dictNodes, dataNodes, mazeImg) :
   ## Inisialisasi Node source pertama
   currSrcNode = 0

   while(currSrcNode < len(dictNodes)) :
       ## Posisi Node source
       currSrcPos = (dataNodes[currSrcNode][0], dataNodes[currSrcNode][1])
       i = 0
       while(i < len(dictNodes[currSrcNode])) :
            ## Node tujuan yang terhubung dengan node source
            currDstNode = dictNodes[currSrcNode][i]
            currDstPos = (dataNodes[currDstNode][0], dataNodes[currDstNode][1])

            ## Warnai edges
            cv2.line(mazeImg, currSrcPos, currDstPos, (0, 0, 200), 1) # Merah

            ##Warnai nodes
            cv2.line(mazeImg, currSrcPos, currSrcPos, (200, 0, 0), 1) # Biru
            cv2.line(mazeImg, currDstPos, currDstPos, (200, 0, 0), 1) # Biru
            i += 1
       currSrcNode += 1

def searchNode(dictNodes, identity) :
    ## Mencari node dalam dictionary node
    isFound = False

    if identity in dictNodes :
        isFound = True

    return isFound

def addNode(dictNodes, dataNodes, identity, posX, posY, way1 = 0, way2 = 0, way3 = 0, way4 = 0) :
    ## Menambahkan node ke list adjency dan list data2 node
    dataNodes[identity] = [posX, posY, way1, way2, way3, way4]
    dictNodes[identity] = []

def searchEdges(dictNodes, identity1, identity2) :
    ## Mencari apakah sudah apa connection antara node1 dan node2
    isFound = False

    if(searchNode(dictNodes, identity1) and searchNode(dictNodes, identity2)) :
        for identity in dictNodes:
            if(identity == identity1) :
                for adjIdentity in dictNodes[identity] :
                    if(adjIdentity == identity2) :
                        isFound = True
                        break
                if(isFound) :
                    break
            elif(identity == identity2) :
                for adjIdentity in dictNodes[identity] :
                    if(adjIdentity == identity1) :
                        isFound = True
                        break
                if(isFound) :
                    break 

    return isFound

def addEdge(dictNodes, identity1, identity2) :
    ## Menambahkan Hubungan antara dua node yang sudah ada di dict nodes
    dictNodes[identity1].append(identity2)
    dictNodes[identity2].append(identity1)

def isJunction(mazeImg, currX, currY) :
    ## Menentutkan apakah suatu kotak dalam gambar tersebut merupakan tempat yang pas untuk menaruh sebuah node baru
    if(np.any(mazeImg[currX][currY]) != 0):
        wayDown = True if(currX + 1 < len(mazeImg) and np.any(mazeImg[currX+1][currY] != 0)) else False
        wayUp = True if(currX != 0 and np.any(mazeImg[currX-1][currY] != 0)) else False
        wayRight = True if(currY + 1 < len(mazeImg[currX]) and np.any(mazeImg[currX][currY+1] != 0)) else False
        wayLeft = True if(currY != 0 and np.any(mazeImg[currX][currY-1] != 0)) else False

        if(not ((wayLeft and wayRight and not (wayDown or wayUp)) or (wayUp and wayDown and not (wayLeft or wayRight)))) :
            return True
        else :
            return False
    else :
        return False

def upperNodeOf(dataNodes, nodeId) :
    ## Mencari node atas terdekat (satu kolom) dari nodeId
    isFound = False
    upNodeId = None
    enum = nodeId

    thisNode = dataNodes[nodeId]
    thisNodeY = thisNode[0]
    enum -= 1

    while(not isFound and enum >= 0):
        if(dataNodes[enum][0] == thisNodeY):
            upNodeId = enum
            isFound = True
        else :
            enum -= 1

    return upNodeId

def leftNodeOf(dataNodes, nodeId) :
    ## Mencari node kiri (satu baris) terdekat dari nodeId
    isFound = False
    leftNodeId = None
    enum = nodeId

    thisNode = dataNodes[nodeId]
    thisNodeX = thisNode[1]
    enum -= 1

    while(not isFound and enum >= 0):
        if(dataNodes[enum][1] == thisNodeX):
            leftNodeId = enum
            isFound = True
        else :
            enum -= 1

    return leftNodeId
        
def nearEndNode(dataNodes, adjList, endNode) :
    distance = math.sqrt((dataNodes[endNode][0]-dataNodes[adjList[0]][0])**2 + (dataNodes[endNode][1]-dataNodes[adjList[0]][1])**2)
    node = adjList[0]
    i = 1
    while i < len(adjList) :
        currDistance = math.sqrt((dataNodes[endNode][0]-dataNodes[adjList[i]][0])**2 + (dataNodes[endNode][1]-dataNodes[adjList[i]][1])**2)
        if distance > currDistance :
            distance = currDistance
            node = adjList[i]

        i += 1

    return node

def solve():
    ### KAMUS
    dataNodes = {}          # Isinya data posisiX, posisiY, up, down, left, right
    dictNodes = {}          # Isinya adjency list
    solveStack = []         # Dipakai untuk depth first search
    vistNodes = []          # Dipakai untuk mencatat apakah Node sudah pernah didatangi
    identity = 0            # Inisialisasi ID Node pertama
   

    ### ALGORITMA
    ## Mempersiapkan image untuk di read
    picName = input("Nama file : ")
    mazeImg = cv2.imread(picName, cv2.IMREAD_COLOR)


    ## Membuat graf dari maze
    startTimer = time.process_time()
    for i in range(0, len(mazeImg)) :
        for j in range(0, len(mazeImg[i])) :
            ## Menentukan apakah pada posisi i, j terdapat sebuah junction, jika ya maka buat node di situ
            if(isJunction(mazeImg, i, j)) :

                ## Menentukan apakah dari node tersebut terdapat jalan ke atas, ke samping, atau ke bawah. Jika terdapat jalan hasilnya 1 (True)
                UP = 1 if(i != 0 and np.any(mazeImg[i-1][j] != 0)) else 0
                DOWN = 1 if(i + 1 < len(mazeImg) and np.any(mazeImg[i+1][j] != 0)) else 0
                LEFT = 1 if(j != 0 and np.any(mazeImg[i][j-1] != 0)) else 0
                RIGHT = 1 if(j + 1 < len(mazeImg[i]) and np.any(mazeImg[i][j+1] != 0)) else 0
                
                ## Menambahkan node di posisi tersebut
                addNode(dictNodes, dataNodes, identity, j, i, UP, DOWN, LEFT, RIGHT) # j, i karena saat di gambarkan, j adalah kolom (X) dan i adalah baris (Y)

                ## Membentuk edges dari node yang baru dibuat dengan node di atasnya dan/atau di kirinya
                if(UP == 1) :
                    upperNode = upperNodeOf(dataNodes, identity)
                    if(upperNode != None) :
                        addEdge(dictNodes, identity, upperNode)
                if(LEFT == 1) :
                    leftNode = leftNodeOf(dataNodes, identity)
                    if(leftNode != None) :
                        addEdge(dictNodes, identity, leftNode)

                identity += 1
    ## Menentukan Start Node dan End Node dari data nodes
    startNode = 0
    endNode = len(dataNodes) - 1 


    ## Bagian untuk beneran solvingnya (pakai depth first search (stack))
    currNode = startNode                    # Current Node
    adjNodes = dictNodes[currNode]          # List of adjacent and unvisited Node from current node
    solveStack.append(currNode)              # Stack to process serve as a path too leading from start to finish
    vistNodes.append(currNode)              # Changging current node to visited
    i = 0
    while(currNode != endNode) :
        
        while(i < len(adjNodes) and currNode != endNode) :
            nextNode = nearEndNode(dataNodes, adjNodes, endNode)
            """
            print("currNode : ", end="", flush=True)
            print(currNode)
            print("nextNode : ", end="", flush=True)
            print(nextNode)
            print("adjNodes : ", end="", flush=True)
            print(adjNodes)
            print("solveStack : ", end="", flush=True)
            print(solveStack)
            """
            if(not (nextNode in vistNodes)) :
                dictNodes[currNode].remove(nextNode)
                """
                print("dictNodes[currNode] : ", end="", flush=True)
                print(dictNodes[currNode])
                """
                currNode = nextNode
                vistNodes.append(currNode)
                solveStack.append(currNode)
                adjNodes = dictNodes[currNode]
                #i = 0

            else :
                dictNodes[currNode].remove(nextNode)
                adjNodes = dictNodes[currNode]
                #i += 1

        if(len(solveStack) > 0 and currNode != endNode) :
            lastNode = solveStack.pop(len(solveStack) - 1)
            """
            print("solveStack : ", end="", flush=True)
            print(solveStack)
            """
            currNode = solveStack[len(solveStack) - 1]
            adjNodes = dictNodes[currNode]
            i = 0
        else :
            break

    if(len(solveStack) > 0) :
        endTimer = time.process_time()
        imgBefore = cv2.imread(picName, cv2.IMREAD_COLOR)
        drawPath(dataNodes, solveStack, mazeImg)
        print("Graphing Time : ", end="", flush=True)
        print(endTimer - startTimer)

        dim = (400, 400)
        mazeImg = cv2.resize(mazeImg, dim, interpolation = cv2.INTER_AREA)
        imgBefore = cv2.resize(imgBefore, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow("after", mazeImg)
        cv2.imshow("before", imgBefore)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else :
        print("There\'s no way from start to finish")  

solve()