import cv2
import numpy as np
import time
import math

def drawPath(dataNodes, solveStack, mazeImg) :
    ## Menggambarkan lintasan yang sudah selesai
    lenStack = len(solveStack)
    i = 0

    while(i + 1 < lenStack) :
        currPos = (dataNodes[solveStack[i]][0], dataNodes[solveStack[i]][1])
        nextPos = (dataNodes[solveStack[i + 1]][0], dataNodes[solveStack[i + 1]][1])
        cv2.line(mazeImg, currPos, nextPos, (100+i/2, i/3, 255-i/2), 1)
        i += 1

def animate(dataNodes, solveStack, picName) :
    tempImg = cv2.imread(picName, cv2.IMREAD_COLOR)
    drawPath(dataNodes, solveStack, tempImg)
    dim = (400, 400)
    rezTemp = cv2.resize(tempImg, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("Solving...", rezTemp)
    cv2.waitKey(1)                              ##Kecepatan animasi

def drawGraph(dictNodes, dataNodes, mazeImg) :
   ## Inisialisasi Node source pertama
   currSrcNode = 0
   lenDict = len(dictNodes)

   while(currSrcNode < lenDict) :
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

def addNode(dictNodes, dataNodes, identity, posX, posY, way1, way2, way3, way4, visited) :
    ## Menambahkan node ke list adjency dan list data node-node
    dataNodes[identity] = [posX, posY, way1, way2, way3, way4, visited]
    dictNodes[identity] = []

def searchEdges(dictNodes, identity1, identity2) :
    ## Mencari apakah sudah ada sisi antara node 1 dan node 2
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
    ## Menentutkan apakah suatu kotak/pixel dalam gambar tersebut merupakan tempat yang pas untuk menaruh sebuah node baru
    lenRow = len(mazeImg)
    lenCol = len(mazeImg[lenRow-1])
    
    if(np.any(mazeImg[currX][currY]) != 0):
        wayDown = True if(currX + 1 < lenRow and np.any(mazeImg[currX+1][currY] != 0)) else False
        wayUp = True if(currX != 0 and np.any(mazeImg[currX-1][currY] != 0)) else False
        wayRight = True if(currY + 1 < lenCol and np.any(mazeImg[currX][currY+1] != 0)) else False
        wayLeft = True if(currY != 0 and np.any(mazeImg[currX][currY-1] != 0)) else False

        if(not ((wayLeft and wayRight and not (wayDown or wayUp)) or (wayUp and wayDown and not (wayLeft or wayRight)))) :
            return True
        else :
            return False
    else :
        return False

def upperNodeOf(dataNodes, nodeId) :
    ## Mencari node atas terdekat (satu kolom) dari nodeId
    upNodeId = None
    enum = nodeId

    thisNode = dataNodes[nodeId]
    thisNodeY = thisNode[0]
    enum -= 1

    while(enum >= 0):
        if(dataNodes[enum][0] == thisNodeY):
            upNodeId = enum
            break
        else :
            enum -= 1

    return upNodeId

def leftNodeOf(dataNodes, nodeId) :
    ## Mencari node kiri (satu baris) terdekat dari nodeId
    leftNodeId = None
    enum = nodeId

    thisNode = dataNodes[nodeId]
    thisNodeX = thisNode[1]
    enum -= 1

    while(enum >= 0):
        if(dataNodes[enum][1] == thisNodeX):
            leftNodeId = enum
            break
        else :
            enum -= 1

    return leftNodeId
        
def nearEndNode(dataNodes, adjList, endNode) :
    ## Mencari node dari dari adjList yang paling dekat dengan titik akhir
    distance = math.sqrt((dataNodes[endNode][0]-dataNodes[adjList[0]][0])**2 + (dataNodes[endNode][1]-dataNodes[adjList[0]][1])**2)
    node = adjList[0]
    i = 1
    lenAdj = len(adjList)

    while i < lenAdj :
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
    identity = 0            # Inisialisasi ID Node pertama
    arrUpNodes = {}         # Menyimpan node teratas dari setiap kolom
    arrLeftNodes = {}       # Menyimpan node terkiri dari setiap baris
   

    ### ALGORITMA
    ## Mempersiapkan image untuk di-read
    picName = input("File name : ")
    mazeImg = cv2.imread(picName, cv2.IMREAD_COLOR)


    ## Mempersiapkan timer dan variable lain
    graphTimer = time.process_time()
    lenRow = len(mazeImg)
    lenCol = len(mazeImg[lenRow-1])

    ## Inisialisasi dictionary arrUpNodes dan arrLeftNodes
    for x in range(0, lenCol) :
        arrLeftNodes[x] = None
    for y in range(0, lenRow) :
        arrUpNodes[y] = None

    ## Membuat graf dari gambar labirin
    for i in range(0, lenRow) :
        for j in range(0, lenCol) :
            ## Menentukan apakah pada posisi i, j terdapat sebuah junction, jika ya maka buat node di situ
            if(isJunction(mazeImg, i, j)) :

                ## Menentukan apakah dari node tersebut terdapat jalan ke atas, ke samping, atau ke bawah. Jika terdapat jalan hasilnya 1 (True)
                UP = 1 if(i != 0 and np.any(mazeImg[i-1][j] != 0)) else 0
                DOWN = 1 if(i + 1 < lenRow and np.any(mazeImg[i+1][j] != 0)) else 0
                LEFT = 1 if(j != 0 and np.any(mazeImg[i][j-1] != 0)) else 0
                RIGHT = 1 if(j + 1 < lenCol and np.any(mazeImg[i][j+1] != 0)) else 0
                
                ## Menambahkan node di posisi tersebut
                addNode(dictNodes, dataNodes, identity, j, i, UP, DOWN, LEFT, RIGHT, False)            # j, i karena saat di gambarkan, j adalah kolom (X) dan i adalah baris (Y)

                ## Membentuk edges dari node yang baru dibuat dengan node di atasnya dan/atau di kirinya
                # Jika ada jalan ke atas
                if(UP == 1) :
                    upperNode = arrUpNodes[dataNodes[identity][0]]
                    if(upperNode != None) :
                        addEdge(dictNodes, identity, upperNode)
                # Jika ada jalan ke kiri
                if(LEFT == 1) :
                    leftNode = arrLeftNodes[dataNodes[identity][1]]
                    if(leftNode != None) :
                        addEdge(dictNodes, identity, leftNode)

                ## Mengupdate arrLeftNodes dan arrUpNodes
                arrLeftNodes[i] = identity
                arrUpNodes[j] = identity

                identity += 1

    ## Menentukan Start Node dan End Node dari data nodes
    startNode = 0
    endNode = len(dataNodes) - 1 

    ## Berurusan dengan waktu proses
    endGraphTimer = time.process_time()
    print("Graphing Time : ", end="", flush=True)
    print(endGraphTimer - graphTimer)
    solveTimer = time.process_time()

    ## Bagian untuk solvingnya (pakai depth first search (stack) ditambah sedikit elemen dari pencariaan jalur terpendek)
    currNode = startNode                    # Current Node
    adjNodes = dictNodes[currNode]          # List of adjacent and unvisited Node from current node
    solveStack.append(currNode)             # Stack to process serve as a path too leading from start to finish
    lenSolve = 1                            # Untuk optimisasi pencarian
    dataNodes[currNode][6] = True           # Changging current node to visited

    while(currNode != endNode) :
        
        while(adjNodes != [] and currNode != endNode) :
            nextNode = nearEndNode(dataNodes, adjNodes, endNode)

            ##Bagian untuk menganimasikan pencarian jalan
            animate(dataNodes, solveStack, picName)

            ## Jika nextNode belum pernah dikunjungi
            if(not (dataNodes[nextNode][6])) :
                dictNodes[currNode].remove(nextNode)
                currNode = nextNode
                dataNodes[nextNode][6] = True
                solveStack.append(currNode)
                lenSolve += 1
                adjNodes = dictNodes[currNode]

            ## Jika nextNode sudah pernah dikunjungi
            else :
                dictNodes[currNode].remove(nextNode)
                adjNodes = dictNodes[currNode]

        ## Jika tidak ada simpul yang bertetanggaan dengan currNode atau semua simpul yang bertetanggaan sudah pernah dikunjungi
        if(lenSolve > 0 and currNode != endNode) :
            lastNode = solveStack.pop(lenSolve - 1)
            lenSolve -= 1
            currNode = solveStack[lenSolve - 1]
            adjNodes = dictNodes[currNode]
        else :
            break

    ## Jika ditemukan lintasan dari titik awal ke titik akhir
    if(lenSolve > 0) :

        ## Menghentikan timer
        endSolveTimer = time.process_time()
        print("Solving (+ Animation)Time : ", end="", flush=True)
        print(endSolveTimer - solveTimer)

        ## Menggambar hasil solusi di gambar labirinnya
        drawPath(dataNodes, solveStack, mazeImg)

        ## Me-resize gambar agar mudah dilihat
        dim = (400, 400)
        mazeImg = cv2.resize(mazeImg, dim, interpolation = cv2.INTER_AREA)
        imgBefore = cv2.imread(picName, cv2.IMREAD_COLOR)
        imgBefore = cv2.resize(imgBefore, dim, interpolation = cv2.INTER_AREA)
        
        ## Menampilkan gambar ke layar
        cv2.destroyAllWindows()
        cv2.imshow("after", mazeImg)
        cv2.imshow("before", imgBefore)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        #cv2.imwrite("rez" + picName, imgBefore)
        #cv2.imwrite("hasilpath" + picName, mazeImg)
        
    ## jika tidak ditemukan lintasan dari titik awal ke titik akhir
    else :
        print("There\'s no way from start to finish")  

solve()