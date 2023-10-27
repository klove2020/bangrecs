import pandas as pd

class Item:
    def __init__(self, dls) -> None:
        self.share = dls
        self.data_ir = None
        self.sid = None
        self.sys_index = None
        self.local_update_time = pd.Timestamp(0)


