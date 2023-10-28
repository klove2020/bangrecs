CREATE TABLE collectForTrain AS 
SELECT * 
FROM collect 
WHERE sid IN (SELECT sid FROM `candidateItemForTrain`) 
AND rate > 0;

ALTER TABLE `collectForTrain` ADD key (`uid`);
ALTER TABLE `collectForTrain` ADD key (`sid`);
ALTER TABLE `collectForTrain` ADD key (`timestamp`);




-- Step 1: 创建新表（这里假设旧表叫 collectForTrain，新表叫 collectForTrain_new）
CREATE TABLE collectForTrain_new LIKE collectForTrain;

-- 修改新表，使得主键ID从0开始自增
ALTER TABLE collectForTrain_new MODIFY id INT AUTO_INCREMENT PRIMARY KEY;

-- Step 2: 从旧表复制数据到新表
INSERT INTO collectForTrain_new (uid, sid, rate, type, subject_type, timestamp, datetime_temp)  
SELECT uid, sid, rate, type, subject_type, timestamp, datetime_temp FROM collectForTrain;

-- Step 3: 删除旧表（请在确保数据已经成功迁移并备份后执行此步骤）
DROP TABLE collectForTrain;

-- Step 4: 将新表重命名为旧表的名称
RENAME TABLE collectForTrain_new TO collectForTrain;



-- ## 添加 c_count
-- ALTER TABLE collectForTrain ADD s_count INT; -- 先为表添加一个s_count列

-- CREATE TEMPORARY TABLE TempCount AS
-- SELECT sid, COUNT(*) as s_count
-- FROM collectForTrain
-- GROUP BY sid;

-- UPDATE collectForTrain
-- JOIN TempCount ON collectForTrain.sid = TempCount.sid
-- SET collectForTrain.s_count = TempCount.s_count;

-- DROP TEMPORARY TABLE TempCount;
