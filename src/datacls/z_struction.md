
data_c
|
|-- df_ir:df交互表
|
|-- df_item_tags
|
|-- df_item_info 
|
|-- df_user_index
|       uid : sys_index : username
|
|-- df_item_index
|       sid : sys_index 
|
|-- attribute
    center_update_time
    active_user_list
    

user
:: share :data_c
:: data_ir
:: uid : user id
:: sys_index 
:: uname: user name
:: local_update_time

:: last_active_time



item
:: share :data_c
:: data_ir
:: sid : item id
:: sys_index
:: local_update_time

:: tags : dict {tag:count}


UI 
    orignize data_c user item