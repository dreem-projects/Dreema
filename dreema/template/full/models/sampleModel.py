from datetime import datetime
from dreema.orm import database

class SampleModel(database.Database):
    #specify table or document name here
    tablename = 'dreema_sample' 

     # system uses default connection type if not specified
    def __init__(self, connection="default"):
        super().__init__(connection=connection)
        self.setTable(self.tablename)