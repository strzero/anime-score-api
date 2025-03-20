import requests
from tqdm import tqdm
import zipfile
import os

def download_bangumi_data():
    """
    下载 Bangumi 数据的 ZIP 文件并解压到 data 文件夹。
    
    成功返回 True，失败返回 False。
    """
    json_url = "https://raw.githubusercontent.com/bangumi/Archive/refs/heads/master/aux/latest.json"
    data_dir = os.path.join("maintain", "data") 

    try:
        # 确保 data 文件夹存在
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 获取 JSON 数据
        response = requests.get(json_url)
        if response.status_code != 200:
            print(f"获取 JSON 数据失败，状态码: {response.status_code}")
            return False
        
        data = response.json()
        download_url = data.get("browser_download_url")  # 获取下载 URL
        
        if not download_url:
            print("未找到 'browser_download_url' 字段！")
            return False

        file_name = os.path.join(data_dir, "bangumi_data.zip")  # 保存 ZIP 文件的路径
        extract_dir = data_dir  # 解压到 data 文件夹

        # 发送请求获取文件大小
        with requests.get(download_url, stream=True) as r:
            total_size = int(r.headers.get("content-length", 0))  # 获取文件总大小
            block_size = 1024  # 每次下载的块大小（1KB）
            
            # 进度条设置
            with open(file_name, "wb") as file, tqdm(
                desc=f"Downloading {file_name}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in r.iter_content(chunk_size=block_size):
                    file.write(chunk)
                    bar.update(len(chunk))  # 更新进度条

        print("下载完成！")

        # 解压文件
        print("正在解压...")
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        print("解压完成！")

        return True  # 成功

    except Exception as e:
        print(f"发生错误: {e}")
        return False  # 失败

# 直接运行
if __name__ == "__main__":
    success = download_bangumi_data()
    if success:
        print("操作成功！")
    else:
        print("操作失败！")
