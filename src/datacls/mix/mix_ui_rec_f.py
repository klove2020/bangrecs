import time
from src.sql.connect import connect_sql
import pandas as pd
from datetime import datetime, timezone, timedelta

class MixUiRec:
    def rec_pop(self, **args):
        days = args.get("popdays", 7)
        topk = args.get("topk", 10)
        sid_list = args.get("candidate_sid", 'all')

        

        if not hasattr(self, 'rec_pop_result'):
            self.rec_pop_result = {}

        t = time.time()
        t = get_midnight_timestamp(t)

        last_updata_t, df = self.rec_pop_result.get(days, (0, 0))

        if t - last_updata_t < 3600 * 24 and topk == 10 and sid_list == "all":
            return df
        else:
            connection, cursor = connect_sql(dict=1)
            seconds = 3600 * 24 * days
            recent_timestamp = t - seconds

            if sid_list == "all":
                sql_sid_cmd = ""
            else:
                if len(sid_list) == 1:
                    sql_sid_cmd = f"AND sid = {sid_list[0]}"    
                else:
                    sql_sid_cmd = f"AND sid IN {tuple(sid_list)}"

            query = f"""
            WITH RankedSids AS (
                SELECT 
                    subject_type, 
                    sid, 
                    COUNT(sid) AS pop,
                    ROW_NUMBER() OVER(PARTITION BY subject_type ORDER BY COUNT(sid) DESC) AS row_num
                FROM collect
                WHERE (timestamp > %s {sql_sid_cmd})
                GROUP BY subject_type, sid
            )
            SELECT 
                rs.subject_type, 
                rs.sid, 
                rs.pop,
                ii.date,
                ii.summary,
                ii.name,
                ii.name_cn,
                ii.rank,
                ii.score,
                ii.nsfw,
                ii.images ->>'$.medium' AS image_medium
            FROM RankedSids AS rs
            JOIN item_info AS ii ON rs.sid = ii.sid
            WHERE (rs.row_num <= {topk} )
            ORDER BY rs.subject_type, rs.pop DESC;
            """

            cursor.execute(query, (recent_timestamp,))
            result = cursor.fetchall()

            # df = pd.DataFrame(result, columns=["subject_type", "sid", "pop"])
            df = pd.DataFrame(result).sort_values(by="pop",ascending=False)

            if topk == 10 and sid_list == "all":
                self.rec_pop_result[days] = (t, df)
            return df



def get_midnight_timestamp(t):
    """
    Convert a timestamp to the midnight timestamp of the same day (UTC+8).
    Args:
    - t (float): The original timestamp.
    Returns:
    - float: The midnight timestamp (UTC+8) of the same day.
    """
    # Convert the timestamp to UTC+8 local time
    local_time = datetime.fromtimestamp(t, tz=timezone(timedelta(hours=8)))
    # Get the midnight time of the same day
    midnight_local = local_time.replace(hour=0, minute=0, second=0, microsecond=0)
    # Convert the local time back to a timestamp
    return midnight_local.timestamp()

