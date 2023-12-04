## 节点
有两类节点，节点相应的字段
* Subject
    * id
    * effectiveTag

* Tag
    * name

例如: 
```
{"<id>":0,"effectiveTag":["爱情","小说"],"id":1,"labels":["Subject"]}

{"<id>":1,"name":"痞子蔡","labels":["Tag"]}
```

## 边
有两类边，HAS_TAG 与 RELATION
* HAS_TAG
    * 条目和tag间的连边
```
{
  "start": {
    "identity": {
      "low": 290376,
      "high": 0
    },
    "labels": [
      "Subject"
    ],
    "properties": {
      "id": {
        "low": 306916,
        "high": 0
      }
    }
  },
  "end": {
    "identity": {
      "low": 1,
      "high": 0
    },
    "labels": [
      "Tag"
    ],
    "properties": {
      "name": "痞子蔡"
    }
  },
  "segments": [
    {
      "start": {
        "identity": {
          "low": 290376,
          "high": 0
        },
        "labels": [
          "Subject"
        ],
        "properties": {
          "id": {
            "low": 306916,
            "high": 0
          }
        }
      },
      "relationship": {
        "identity": {
          "low": 1322848,
          "high": 0
        },
        "start": {
          "low": 290376,
          "high": 0
        },
        "end": {
          "low": 1,
          "high": 0
        },
        "type": "HAS_TAG",
        "properties": {
          "count": {
            "low": 1,
            "high": 0
          }
        }
      },
      "end": {
        "identity": {
          "low": 1,
          "high": 0
        },
        "labels": [
          "Tag"
        ],
        "properties": {
          "name": "痞子蔡"
        }
      }
    }
  ],
  "length": 1
}
```

* RELATION
    * 条目间的关联
```
{
  "start": {
    "identity": {
      "low": 282691,
      "high": 0
    },
    "labels": [
      "Subject"
    ],
    "properties": {
      "id": {
        "low": 296317,
        "high": 0
      }
    }
  },
  "end": {
    "identity": {
      "low": 0,
      "high": 0
    },
    "labels": [
      "Subject"
    ],
    "properties": {
      "effectiveTag": [
        "爱情",
        "小说"
      ],
      "id": {
        "low": 1,
        "high": 0
      }
    }
  },
  "segments": [
    {
      "start": {
        "identity": {
          "low": 282691,
          "high": 0
        },
        "labels": [
          "Subject"
        ],
        "properties": {
          "id": {
            "low": 296317,
            "high": 0
          }
        }
      },
      "relationship": {
        "identity": {
          "low": 2040782,
          "high": 0
        },
        "start": {
          "low": 282691,
          "high": 0
        },
        "end": {
          "low": 0,
          "high": 0
        },
        "type": "RELATION",
        "properties": {
          "type": {
            "low": 1,
            "high": 0
          },
          "order": {
            "low": 0,
            "high": 0
          }
        }
      },
      "end": {
        "identity": {
          "low": 0,
          "high": 0
        },
        "labels": [
          "Subject"
        ],
        "properties": {
          "effectiveTag": [
            "爱情",
            "小说"
          ],
          "id": {
            "low": 1,
            "high": 0
          }
        }
      }
    }
  ],
  "length": 1
}
```

## 更新逻辑
暂不更新