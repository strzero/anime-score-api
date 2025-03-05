from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class IdLink(models.Model):
    bangumi_id = fields.IntField(pk=True, index=True)
    myanimelist_id = fields.CharField(max_length=255, null=True)
    anilist_id = fields.CharField(max_length=255, null=True)
    filmarks_id = fields.CharField(max_length=255, null=True)
    anikore_id = fields.CharField(max_length=255, null=True)
    user_add = fields.IntField(null=True)
    verification_count = fields.IntField(null=True)

    class Meta:
        table = "id_link"

    def __str__(self):
        return f"IdLink(bangumi_id={self.bangumi_id})"

# 自动生成 Pydantic 模型，用于数据验证和序列化
IdLink_Pydantic = pydantic_model_creator(IdLink, name="IdLink")
IdLinkIn_Pydantic = pydantic_model_creator(IdLink, name="IdLinkIn", exclude=("bangumi_id",))

class Score(models.Model):
    bangumi_id = fields.IntField(pk=True, index=True)
    update_time = fields.DatetimeField()
    expire_time = fields.DatetimeField()
    myanimelist_name = fields.CharField(max_length=255, null=True)
    myanimelist_score = fields.FloatField(null=True)
    myanimelist_count = fields.IntField(null=True)
    myanimelist_id = fields.CharField(max_length=255, null=True)
    anilist_name = fields.CharField(max_length=255, null=True)
    anilist_score = fields.FloatField(null=True)
    anilist_count = fields.IntField(null=True)
    anilist_id = fields.CharField(max_length=255, null=True)
    filmarks_name = fields.CharField(max_length=255, null=True)
    filmarks_score = fields.FloatField(null=True)
    filmarks_count = fields.IntField(null=True)
    filmarks_id = fields.CharField(max_length=255, null=True)
    anikore_name = fields.CharField(max_length=255, null=True)
    anikore_score = fields.FloatField(null=True)
    anikore_count = fields.IntField(null=True)
    anikore_id = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "score"

    def __str__(self):
        return f"Score(bangumi_id={self.bangumi_id}, update_time={self.update_time})"

# 自动生成 Pydantic 模型，用于数据验证和序列化
Score_Pydantic = pydantic_model_creator(Score, name="Score")
ScoreIn_Pydantic = pydantic_model_creator(Score, name="ScoreIn", exclude=("bangumi_id",))
