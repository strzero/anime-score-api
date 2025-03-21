from typing import List
from fastapi import APIRouter, Query
from sympy import Q
import re

from models.db_model import BangumiData
from models.response_model import BangumiResponse

router = APIRouter()

@router.get("/search", response_model=List[BangumiResponse])
async def search_bangumi(query: str = Query(..., min_length=1)) -> List[dict]:
    # 定义日文假名的正则表达式，匹配平假名和片假名
    japanese_regex = re.compile(r'[\u3040-\u30ff]')

    # 检查查询字符是否包含日文假名
    if japanese_regex.search(query):
        # 如果包含日文假名，则使用 name 字段进行搜索
        bangumi_data = await BangumiData.filter(name__icontains=query).all()
    else:
        # 否则，使用 name_cn 字段进行搜索
        bangumi_data = await BangumiData.filter(name_cn__icontains=query).all()

    # 按相关性排序：这里简单通过 score 来排序
    sorted_data = sorted(bangumi_data, key=lambda x: x.score, reverse=True)

    # 构造响应数据
    response_data = []
    for item in sorted_data:
        response_data.append({
            "id": item.id,
            "name": item.name,
            "name_cn": item.name_cn,
            "date": item.date,
            "score": item.score
        })
    
    return response_data