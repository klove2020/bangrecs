[toc]

# 用户条目交互数据
* 最核心的数据库
## 1. collect 表
update in 23.12.3
### 用途
- 用于记录用户对条目的收藏信息。
- 存储用户行为数据，用于分析用户偏好及推荐系统的输入，是推荐模型训练数据的数据源。

### 列描述

- `id`：收藏记录的唯一标识符，数据类型为int。
- `uid`：用户的唯一标识符，数据类型为int。
- `sid`：条目的唯一标识符，数据类型为int。
- `rate`：用户给条目的评分，数据类型为int。
- `type`：收藏类型的编号，数据类型为int。
- `subject_type`：条目类型的编号，数据类型为int。
- `timestamp`：收藏事件的时间戳，数据类型为int。
- `datetime_temp`：收藏时间的日期时间表示，数据类型为datetime。

### 数据示例
下表展示了八列数据，分别为 `id`，`uid`，`sid`，`rate`，`type`，`subject_type`，`timestamp`，和 `datetime_temp`。

| id | uid | sid  | rate | type | subject_type | timestamp | datetime_temp         |
|-----|-----|------|------|------|--------------|-----------|-----------------------|
| 1   | 2   | 2    | 0    | 2    | 3            | 1290435093| 2010-11-22 14:11:33   |
| 2   | 2   | 1836 | 0    | 2    | 2            | 1288849903| 2011-04-05 05:14:43   |
| 3   | 2   | 4    | 0    | 2    | 4            | 1232774083| 2009-01-24 05:14:43   |
| 4   | 3   | 1836 | 0    | 1    | 2            | 1216023643| 2008-07-14 08:20:43   |
| 5   | 1   | 4    | 0    | 2    | 4            | 1234423357| 2009-02-12 07:22:37   |

### 更新逻辑
- 每天随机更新10000个活跃用户的收藏记录， airflow 自动更新函数位于 [src/sql/sql_update_f.py](../src/sql/sql_update_f.py)
- 使用推荐系统的用户收藏将被更新

## 2. item_info 表
update in 23.12.3
### 用途
- 存储条目的详细信息，包括名称、评分、标签等。
- 为用户提供条目相关的详细数据，以支持决策过程。

### 列描述

- `id`：条目信息的唯一标识符，数据类型为int。
- `sid`：与条目相关的系统唯一标识符，数据类型为int。
- `date`：条目发布日期，数据类型为date。
- `platform`：条目所在平台，数据类型为varchar(255)。
- `summary`：条目概述，数据类型为text。
- `name`：条目的英文名称，数据类型为varchar(255)。
- `name_cn`：条目的中文名称，数据类型为varchar(255)。
- `tags`：条目相关的标签，数据类型为json。
- `infobox`：条目信息框内容，数据类型为json。
- `rank`：条目的排名，数据类型为int。
- `total`：条目的总数，数据类型为int。
- `count`：相关计数信息，数据类型为json。
- `score`：条目的评分，数据类型为float。
- `total_episodes`：条目的总集数，数据类型为int。
- `collection`：收藏信息，数据类型为json。
- `eps`：已发布的集数或期数，数据类型为int。
- `volumes`：条目的总卷数，数据类型为int。
- `locked`：条目是否被锁定，数据类型为tinyint(1)。
- `nsfw`：是否为成人内容，数据类型为tinyint(1)。
- `type`：条目类型，数据类型为varchar(255)。
- `images`：条目相关的图片，数据类型为json。

### 数据示例
下表展示了部分列的数据。

| id  | sid | date       | platform | summary            | name                       | name_cn           | tags                         | infobox              | rank | score |
|-----|-----|------------|----------|--------------------|----------------------------|-------------------|------------------------------|----------------------|------|-------|
| 1   | 1   | 1998-09-25 | 小说     | 最具影响力的奇幻... | 一次的冒险旅程            | 一次的奇幻旅程   | [{"name": "奇幻", "count... | [{"key": "中文名",... | 1468 | 7.7   |
| ... | ... | ...        | ...      | ...                | ...                        | ...               | ...                          | ...                  | ...  | ...   |

(请注意，数据示例仅显示了部分列，完整的数据示例应包含所有列的示例数据。)

### 更新逻辑
- 只维护新数据，不维护旧数据。由近期collect来决定哪些条目被更新 / 增加。
- airflow 自动更新函数位于 [src/sql/sql_update_f.py](../src/sql/sql_update_f.py)

# 查询表层面
* 系统中多数时候需要进行多次查询使用的表格

## 1. candidateItem 表
update in 23.12.3
### 用途
- 作为推荐系统候选项的集合。用于存储可能被推荐的项目，以供进一步的评分和筛选。
- 是几乎所有推荐算法过滤条目候选列表时最先查询的表, _get_candidate_list函数中使用位于文件[  src/Backend/util/filting_f.py](../src/Backend/util/filting_f.py)

### 列描述

- `subject_type`：条目类型的编号，数据类型为bigint。
- `sid`：条目的唯一标识符，数据类型为bigint。
- `date`：条目的发布日期，数据类型为datetime。
- `rank`：条目的排名，数据类型为bigint。
- `score`：条目的评分，数据类型为double。
- `nsfw`：条目是否为成人内容，数据类型为bigint，其中0代表非成人内容。

### 数据示例
下表展示了六列数据，分别为 `subject_type`，`sid`，`date`，`rank`，`score` 和 `nsfw`。

| subject_type | sid | date                | rank | score | nsfw |
|--------------|-----|---------------------|------|-------|------|
| 1            | 1   | 1998-09-25 00:00:00 | 1468 | 7.7   | 0    |
| 4            | 4   | 2008-07-17 00:00:00 | 3990 | 6.9   | 0    |
| 4            | 6   | 2007-10-10 00:00:00 | 1690 | 7.5   | 0    |
| 2            | 8   | 2008-04-06 00:00:00 | 98   | 8.2   | 0    |
| 4            | 9   | 2008-07-31 00:00:00 | 240  | 8.3   | 0    |

### 更新逻辑
- 更新函数位于文件 [src/sql/F.py](../src/sql/F.py)。
- 更新策略是基于用户的行为和反馈，以及项目的当前热度和相关性。
- (**TODO: airflow 流水线更新, 运行更新函数即可**)





## 2. SubjectRelations 表
update in 23.12.3

### 用途
* 作为 [src/model/F/rec.py](../src/model/F/rec.py) 过滤函数(check_sid_list) 中检验关联作品是否有差评主要的查询表
* 作为转移模型中关联条目的主要查询表
* 备注: **TODO: 该表后期将被neo4j数据库取代**

### 列描述

- `subject_id`：条目的唯一标识符，数据类型为int。
- `relation_type`：关系类型的编号，数据类型为int。参考[类型与关系说明](类型与关系文档.txt)
- `related_subject_id`：相关条目的唯一标识符，数据类型为int。
- `order_num`：排序编号，数据类型为int。继承自bangumi归档数据。（不重要）

### 数据示例
下表展示了四列数据，分别为 `subject_id`，`relation_type`，`related_subject_id` 和 `order_num`。

| subject_id | relation_type | related_subject_id | order_num |
|------------|---------------|--------------------|-----------|
| 1          | 1             | 296317             | 0         |
| 4          | 4002          | 9944               | 0         |
| 4          | 4006          | 9950               | 0         |
| 6          | 4099          | 108488             | 0         |
| 6          | 4002          | 121872             | 0         |

### 更新逻辑
* 不更新, 后面可能会弃用该表，数据使用23年的关联数据




## 3. _cache_tags_list 表
update in 23.12.3
### 用途
- 用于API返回tag列表作为前端自动补全候选项，函数 get_effectivetags_list 位于 [src/sql/query_f.py](../src/sql/query_f.py)

### 列描述

- `tag`：标签的名称，数据类型为text。

### 数据示例
下表展示了一列数据，即 `tag`。

| tag  |
|------|
| 绘画 |
| 三次元 |
| 国产 |
| 网文 |
| 轻小说 |
| 少女漫 |

### 更新逻辑
- 构建neo4j effective tag时生成的，后续还未更新 (可以接受较长时间不更新)



## 4. user_mapping 表格
update in 23.12.3

### 用途
- 用于将用户的唯一标识符（UID）映射到其用户名（uname）。

### 列描述
- `uid`：用户的唯一标识符，数据类型为int。
- `uname`：用户的用户名，数据类型为varchar(255)。

### 数据示例
下表展示了两列数据，分别为 `uid` 和 `uname`。

| uid    | uname          |
|--------|----------------|
| 753743 | interestingexm |
| 112992 | intgoo         |
| 179761 | intptr         |
| 733605 | intrigore      |
| ...    | ...            |

(注：示例数据仅展示了表中的一部分记录，实际表可能包含更多的用户数据。)

### 更新逻辑
- 出现未知用户时，会请求bangumi.tv用户页面来自动更新映射, 位于文件 [src/data_spider_mysql/user_mapping_f.py](../src/data_spider_mysql/user_mapping_f.py)中的 update_sql_by_uid 函数.




# 支撑模型类表
* 运行相关模型依赖于这些表格

## 1. HT_item_list 表
update in 23.12.3
### 用途
- 作为HT模型的推荐和训练候选集
- 备注: 只作为可视化记录，模型真正调用的数据源位于 data/filting_data, [HT模型](../src/model/HT_dir/HT_f.py)中的 _item_sid_list_init 方法
### 列描述

- `sid`：唯一标识符，数据类型为bigint。
- `subject_type`：条目类型的编号，数据类型为bigint。
- `class`：类别名称，数据类型为文本。


### 数据示例
下表展示了三列数据，分别为 `sid`，`subject_type` 和 `class`。

| sid  | subject_type | class  |
|------|--------------|--------|
| 4473 | 2            | anime  |
| 4475 | 2            | anime  |
| 4480 | 2            | anime  |
| 4486 | 2            | anime  |
| 4841 | 2            | anime  |

### 更新逻辑
* 更新函数 HT.HT_item_list_table 在文件 [src/model/HT_dir/HT_f.py](../src/model/HT_dir/HT_f.py)。
* 每次初始化HT模型会重写整个表, 依赖于 data/filting_data 中的分类数据，需要手动划分 (**TODO: airflow 流水线更新数据源**)



## 2. trans_ma 表
update in 23.12.3

### 用途
- 存储条目间的转移得分，用于推荐系统或类似应用。
- 记录了从一个条目转移到另一个条目的预计得分，可能基于用户行为或条目相似度。

### 列描述
- `sid`：起始条目的唯一标识符，数据类型为int。
- `trans_sid`：目标条目的唯一标识符，数据类型为int。
- `trans_score`：转移得分，表示从起始条目转移到目标条目的相对可能性，数据类型为float。

### 数据示例
下表展示了三列数据，分别为 `sid`，`trans_sid` 和 `trans_score`。

| sid | trans_sid | trans_score |
|-----|-----------|-------------|
| 1   | 13        | 0.0181327   |
| 1   | 49        | 0.063739    |
| 1   | 309       | 0.158105    |
| 1   | 513       | 0.0190618   |
| ... | ...       | ...         |

(注：示例数据表中只展示了部分记录，实际表中应该包含更多行数据。)

### 更新逻辑
- 训练 seqtransfer 模型得到该表
- (**TODO: 定期 retrain 模型。**)

## 其他表格

* src/sql/sql_item_pop_f.py 中提供关于 item_pop, item_pop_stat的支持，用于转移模型训练时的流行度去偏支持

* post_details, threads 中记录小组讨论

* 不再使用的表：candidateItemForTrain, collectForTrain, feedback_dislike

*  trans_ma_v0, trans_ma_v1, trans_ma_v2: 先前版本的trans_ma表格