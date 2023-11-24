```
src/sql/connect.py : 实现connect_sql 函数，提供python和sql的接口交互

src/sql/F.py:
    get_rec_candidate_list: query = "SELECT sid FROM item_info WHERE (`rank` > 0) AND (`date` IS NOT NULL) AND (locked = 0);"
    writ2sql: 缓存推荐的sid list, candidateItem



```