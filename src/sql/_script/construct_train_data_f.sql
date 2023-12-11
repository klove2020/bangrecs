SELECT c.uid, c.sid, c.rate, c.type, c.subject_type, c.timestamp, h.class
INTO OUTFILE '/var/lib/mysql-files/output_train.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
FROM collect c
JOIN HT_item_list h ON c.sid = h.sid;

-- sudo mv /var/lib/mysql-files/output_train.csv .
-- chmod 666 output_train.csv 