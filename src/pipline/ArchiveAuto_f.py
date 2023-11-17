from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests
import zipfile
import os

# 函数来检查 GitHub 上的最新发布
def check_for_update(ti):
    url = 'https://api.github.com/repos/bangumi/Archive/releases/latest'
    response = requests.get(url)
    response.raise_for_status()
    latest_release = response.json()
    # 将最新的 zip 文件的 URL 传递给下一个任务
    ti.xcom_push(key='download_url', value=latest_release['assets'][0]['browser_download_url'])

# 函数来下载最新的 zip 文件
def download_file(ti):
    download_url = ti.xcom_pull(key='download_url', task_ids='check_for_update')
    local_filename = '/home/klion/bgmrec/data/ArchiveAutoUpdate/dump.zip'
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return local_filename

# 函数来解压缩文件
def unzip_file(**kwargs):
    local_filename = kwargs['ti'].xcom_pull(task_ids='download_file')
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall('/home/klion/bgmrec/data/ArchiveAutoUpdate')
    os.remove(local_filename)  # 删除 zip 文件

# 设置默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 定义 DAG
dag = DAG(
    'bangumi_archive_auto_update',
    default_args=default_args,
    description='A DAG to automatically update Bangumi archive data',
    schedule_interval=timedelta(days=14),  
    start_date=days_ago(1),
    catchup=False,
)

# 创建任务
check_for_update_task = PythonOperator(
    task_id='check_for_update',
    python_callable=check_for_update,
    provide_context=True,
    dag=dag,
)

download_file_task = PythonOperator(
    task_id='download_file',
    python_callable=download_file,
    provide_context=True,
    dag=dag,
)

unzip_file_task = PythonOperator(
    task_id='unzip_file',
    python_callable=unzip_file,
    provide_context=True,
    dag=dag,
)

# 设置任务依赖关系
check_for_update_task >> download_file_task >> unzip_file_task
