from texttable import *
from Foundation import *

import subprocess

import csv
class BColors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
nodes = []

def readNodesToAwake():
    with open('config2.csv', newline='') as csvfile:

        nodesCSV = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in nodesCSV:
            if row[0] !='Node_ip':
                node = []
                node.append(row[0])
                node.append(row[1])
                node.append(row[2])
                nodes.append(node)
def printNodesToAwake():
    print("Nodos que vamos a despertar")
    table = Texttable()
    table.set_cols_align(["c", "c","c" ])
    table.set_cols_valign(["m", "m","m"])
    table.add_row([
    "ip",
    "Puerto",
    "Mascara"])

    for i in range (0,len(nodes)):
        ip = nodes[i][0]
        mascara = nodes[i][1]
        puerto = nodes[i][2]
        table.add_row([ip,puerto,mascara])


    print (table.draw() + "\n")
def awake():
    appleScript = ""
    flag_users = False
    path = ""

    ## We decide which path we want to use, depending on the user.
    while flag_users == False:
        print(BColors.WARNING + "Lista de Usuarios - Path " +BColors.ENDC)
        print("1 - Barrantes")
        print("2 - Flasterstein")
        print("3 - Cruz")
        usuario = input("Número de usuario: ")
        if usuario == "1":
            path = "/Users/paulobarrantes/Proyectos/Tarea1-Redes/Fase3"
            flag_users = True
        elif usuario == "2":
            path = "/Users/Fla/Documents/GitHub/Tarea1-Redes/Fase3"
            flag_users = True


    for i in range (0,len(nodes)):
        ip = nodes[i][0]
        puerto = nodes[i][2]

        appleScript = '''
tell application \"Terminal\"
	set currentTab to do script (\"open -a Terminal\")
	delay 1
	do script (\" cd '''+path+'''\") in currentTab
    delay 1
	do script (\"python3 crearNodo.py -intAS '''+ ip + ''' '''+puerto+'''\") in currentTab

end tell
'''

        s = NSAppleScript.alloc().initWithSource_(appleScript)
        s.executeAndReturnError_(None)


    #subprocess.Popen("python3 prueba.py",creationflags = subprocess.CREATE_NEW_CONSOLE ,shell=True)

readNodesToAwake()
printNodesToAwake()
awake()
