# 运行

## Docker

```python
docker run -d --name anime-score-api -p 5100:5100 --add-host host.docker.internal:host-gateway -e AS_DB_URL=mysql://root:123456@host.docker.internal:3306/anime-score stellatezero/anime-score-api
```

