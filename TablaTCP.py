class TablaTCP():

    def __init__(self):
        self.table = {}

    def save_connection(self, ip, port, connectionSocket):
        self.table.update({(ip,port): connectionSocket})

    def search_connection(self, ip, port):
        if self.table.get((ip,port)):
            return self.table.get((ip,port))
        return -1

    def close_connection(self, ip, port):
        if self.table.get((ip, port)):
            self.table.get((ip, port)).close()
            self.table.pop((ip, port))
