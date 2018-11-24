from texttable import *
from Foundation import *

import subprocess

import csv
class bcolors:

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
    with open('NodesToAwake.csv', newline='') as csvfile:

        nodesCSV = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in nodesCSV:
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
        puerto = nodes[i][1]
        mascara = nodes[i][2]
        table.add_row([ip,puerto,mascara])


    print (table.draw() + "\n")
def awake():
    appleScript = ""

    for i in range (0,len(nodes)):
        puerto = nodes[i][1]
        appleScript = '''
tell application \"Terminal\"
	set currentTab to do script (\"open -a Terminal\")
	delay 1
	do script (\"cd /Users/Fla/Documents/GitHub/Tarea1-Redes\") in currentTab
	do script (\"python3 crearNodo.py -pseudoTCP 127.0.0.1 '''+ puerto +'''\") in currentTab
	do script (\"4\") in currentTab
end tell
'''

        s = NSAppleScript.alloc().initWithSource_(appleScript)
        s.executeAndReturnError_(None)


    #subprocess.Popen("python3 prueba.py",creationflags = subprocess.CREATE_NEW_CONSOLE ,shell=True)

readNodesToAwake()
printNodesToAwake()
awake()
