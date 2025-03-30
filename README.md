# 运行

## Docker

```python
docker run -d --name anime-score-api -p 5100:5100 --add-host host.docker.internal:host-gateway -e AS_DB_URL=mysql://root:123456@host.docker.internal:3306/anime-score stellatezero/anime-score-api
```

其中AS_DB_URL指定数据库信息，host.docker.internal代表主机localhost。

### 手动部署

```shell
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 5100
```

