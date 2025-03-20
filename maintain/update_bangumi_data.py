import os
import json
import pymysql
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urlparse

# 从环境变量获取数据库信息并解析
def parse_db_url(db_url):
    """ 解析数据库连接字符串并返回字典形式的数据库配置 """
    parsed_url = urlparse(db_url)
    return {
        "host": parsed_url.hostname,
        "port": parsed_url.port,
        "user": parsed_url.username,
        "password": parsed_url.password,
        "database": parsed_url.path.lstrip('/')
    }

# 解析日期格式
def format_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def update_bangumi_data():
    """ 从JSONL文件更新数据库中的Bangumi数据，并返回操作结果 True 或 False """

    # 获取数据库配置
    db_url = os.getenv("AS_DB_URL")  # 获取环境变量中的数据库URL
    if not db_url:
        print("❌ 数据库 URL 未设置！")
        return False
    
    # 解析数据库信息
    DB_CONFIG = parse_db_url(db_url)
    
    # 连接数据库
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

    # 确保表存在
    try:
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS bangumi_data (
                id INT PRIMARY KEY,
                type INT,
                name VARCHAR(255),
                name_cn VARCHAR(255),
                infobox TEXT,
                platform INT,
                summary TEXT,
                nsfw BOOLEAN,
                date DATE,
                favorite_wish INT,
                favorite_done INT,
                favorite_doing INT,
                favorite_on_hold INT,
                favorite_dropped INT,
                series BOOLEAN,
                score FLOAT,
                rank_number INT,
                score_1 INT,
                score_2 INT,
                score_3 INT,
                score_4 INT,
                score_5 INT,
                score_6 INT,
                score_7 INT,
                score_8 INT,
                score_9 INT,
                score_10 INT
            )
        """)
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS bangumi_tags (
                bangumi_id INT,
                tag VARCHAR(255),
                PRIMARY KEY (bangumi_id, tag),
                FOREIGN KEY (bangumi_id) REFERENCES bangumi_data(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"❌ 表创建失败: {e}")
        cursor.close()
        conn.close()
        return False

    # 获取当前数据库最大 ID（判断是否需要更新数据）
    cursor.execute("SELECT MAX(id) FROM bangumi_data")
    last_id = cursor.fetchone()[0] or 0  # 如果为空，从 0 开始
    print(f"🔍 断点检测：当前数据库最大 ID = {last_id}")

    # 读取 JSONL 文件并获取数据量
    data_file = os.path.join("maintain", "data", "subject.jsonlines")  # 更新文件路径到 data 目录
    batch_size = 1000
    batch = []
    tag_batch = []

    # 获取记录数
    with open(data_file, "r", encoding="utf-8") as f:
        total_records = sum(1 for _ in f)

    # 开始导入数据
    try:
        with open(data_file, "r", encoding="utf-8") as f, tqdm(total=total_records, desc="导入进度", unit="条") as pbar:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # **只处理 type = 2 的记录**
                    if data["type"] != 2:
                        pbar.update(1)
                        continue

                    # **更新已有记录，不跳过**
                    values = (
                        data["id"], data["type"], data["name"], data["name_cn"], data["infobox"],
                        data["platform"], data["summary"], data["nsfw"],
                        format_date(data["date"]),
                        data["favorite"]["wish"], data["favorite"]["done"], data["favorite"]["doing"],
                        data["favorite"]["on_hold"], data["favorite"]["dropped"], data["series"],
                        data["score"], data["rank"],
                        data["score_details"].get("1", 0), data["score_details"].get("2", 0),
                        data["score_details"].get("3", 0), data["score_details"].get("4", 0),
                        data["score_details"].get("5", 0), data["score_details"].get("6", 0),
                        data["score_details"].get("7", 0), data["score_details"].get("8", 0),
                        data["score_details"].get("9", 0), data["score_details"].get("10", 0)
                    )

                    batch.append(values)

                    # **准备插入 tags 到 tag_batch**
                    for tag in data.get("tags", []):  # 使用 get() 确保即使没有 tags 也不报错
                        tag_batch.append((data["id"], tag["name"]))  # 仅提取 name 字段

                    # **批量插入**
                    if len(batch) >= batch_size:
                        # 使用 REPLACE INTO 来覆盖现有数据
                        cursor.executemany(""" 
                            REPLACE INTO bangumi_data (
                                id, type, name, name_cn, infobox, platform, summary, nsfw, date,
                                favorite_wish, favorite_done, favorite_doing, favorite_on_hold, favorite_dropped, series,
                                score, rank_number,
                                score_1, score_2, score_3, score_4, score_5, score_6, score_7, score_8, score_9, score_10
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, batch)

                        # 插入 tags 表，使用 REPLACE INTO 来覆盖现有数据
                        if tag_batch:  # 确保 tag_batch 非空
                            # print(f"⏳ 插入 tags 数据，共 {len(tag_batch)} 条数据")
                            cursor.executemany(""" 
                                REPLACE INTO bangumi_tags (bangumi_id, tag) VALUES (%s, %s)
                            """, tag_batch)
                            conn.commit()

                        batch.clear()
                        tag_batch.clear()

                    pbar.update(1)

                except Exception as e:
                    print(f"\n❌ 跳过错误数据: {e}")

        # **插入剩余数据**
        if batch:
            cursor.executemany(""" 
                REPLACE INTO bangumi_data (
                    id, type, name, name_cn, infobox, platform, summary, nsfw, date,
                    favorite_wish, favorite_done, favorite_doing, favorite_on_hold, favorite_dropped, series,
                    score, rank_number,
                    score_1, score_2, score_3, score_4, score_5, score_6, score_7, score_8, score_9, score_10
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, batch)
            if tag_batch:  # 确保 tag_batch 非空
                print(f"⏳ 插入剩余 tags 数据，共 {len(tag_batch)} 条数据")
                cursor.executemany(""" 
                    REPLACE INTO bangumi_tags (bangumi_id, tag) VALUES (%s, %s)
                """, tag_batch)
                conn.commit()

        cursor.close()
        conn.close()

        print("\n✅ 数据导入完成！")
        return True  # 成功

    except Exception as e:
        print(f"❌ 数据导入过程中发生错误: {e}")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return False  # 失败

# 直接运行或调用
if __name__ == "__main__":
    success = update_bangumi_data()
    if success:
        print("✅ 操作成功！")
    else:
        print("❌ 操作失败！")
