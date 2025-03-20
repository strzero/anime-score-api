# --------------------------
# update_bangumi_data可实现初始化功能（理论上），如果报错再考虑此版本
# --------------------------
import json
import pymysql
from tqdm import tqdm
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    "host": "154.12.21.182",
    "port": 13306,
    "user": "root",
    "password": "so6666",
    "database": "anime-score"
}

# 解析日期格式
def format_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

# 连接数据库
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 确保表存在
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

# **检测断点（获取当前数据库最大 ID）**
cursor.execute("SELECT MAX(id) FROM bangumi_data")
last_id = cursor.fetchone()[0] or 0  # 如果为空，从 0 开始
print(f"🔍 断点检测：当前数据库最大 ID = {last_id}")

# 读取 JSONL 文件
data_file = "subject.jsonlines"
batch_size = 1000
batch = []
tag_batch = []
total_records = 525481

with open(data_file, "r", encoding="utf-8") as f, tqdm(total=total_records, desc="导入进度", unit="条") as pbar:
    for line in f:
        try:
            data = json.loads(line.strip())

            # **只处理 type = 2 的记录**
            if data["type"] != 2:
                pbar.update(1)
                continue

            # **跳过已存数据（仅插入没有插入过的 bangumi_data）**
            if data["id"] <= last_id:
                # 直接插入tags，不影响
                for tag in data.get("tags", []):  # 确保即使没有 tags 也不报错
                    tag_batch.append((data["id"], tag["name"]))  # 仅提取 name 字段
                pbar.update(1)
                continue  

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
                # 插入 bangumi_data 表，使用 INSERT IGNORE 来避免重复插入
                cursor.executemany("""
                    INSERT IGNORE INTO bangumi_data (
                        id, type, name, name_cn, infobox, platform, summary, nsfw, date,
                        favorite_wish, favorite_done, favorite_doing, favorite_on_hold, favorite_dropped, series,
                        score, rank_number,
                        score_1, score_2, score_3, score_4, score_5, score_6, score_7, score_8, score_9, score_10
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, batch)

                # 插入 tags 表，使用 INSERT IGNORE 来避免重复插入
                if tag_batch:  # 确保 tag_batch 非空
                    print(f"⏳ 插入 tags 数据，共 {len(tag_batch)} 条数据")
                    cursor.executemany("""
                        INSERT IGNORE INTO bangumi_tags (bangumi_id, tag) VALUES (%s, %s)
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
        INSERT IGNORE INTO bangumi_data (
            id, type, name, name_cn, infobox, platform, summary, nsfw, date,
            favorite_wish, favorite_done, favorite_doing, favorite_on_hold, favorite_dropped, series,
            score, rank_number,
            score_1, score_2, score_3, score_4, score_5, score_6, score_7, score_8, score_9, score_10
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, batch)
    if tag_batch:  # 确保 tag_batch 非空
        print(f"⏳ 插入剩余 tags 数据，共 {len(tag_batch)} 条数据")
        cursor.executemany("""
            INSERT IGNORE INTO bangumi_tags (bangumi_id, tag) VALUES (%s, %s)
        """, tag_batch)
        conn.commit()

cursor.close()
conn.close()

print("\n✅ 数据导入完成！")
