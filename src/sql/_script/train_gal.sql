mysql> SELECT sid 
    FROM item_info 
    WHERE `type` LIKE '%4%' 
      AND `tags` LIKE '%galgame%' 
      AND `rank` > 0 
      AND `total` > 100 
      AND `date` > '2004-1-1' 
    INTO OUTFILE '/var/lib/mysql-files/out_gal.csv' 
    FIELDS TERMINATED BY ',' 
    ENCLOSED BY '"' 
    LINES TERMINATED BY '\n';