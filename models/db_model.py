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

Score_Pydantic = pydantic_model_creator(Score, name="Score")
ScoreIn_Pydantic = pydantic_model_creator(Score, name="ScoreIn", exclude=("bangumi_id",))

class BangumiData(models.Model):
    id = fields.IntField(pk=True, index=True)
    type = fields.IntField()
    name = fields.CharField(max_length=255)
    name_cn = fields.CharField(max_length=255)
    infobox = fields.TextField()
    platform = fields.IntField()
    summary = fields.TextField()
    nsfw = fields.IntField()
    date = fields.DateField()
    favorite_wish = fields.IntField()
    favorite_done = fields.IntField()
    favorite_doing = fields.IntField()
    favorite_on_hold = fields.IntField()
    favorite_dropped = fields.IntField()
    series = fields.IntField()
    score = fields.FloatField()
    rank_number = fields.IntField()
    score_1 = fields.IntField()
    score_2 = fields.IntField()
    score_3 = fields.IntField()
    score_4 = fields.IntField()
    score_5 = fields.IntField()
    score_6 = fields.IntField()
    score_7 = fields.IntField()
    score_8 = fields.IntField()
    score_9 = fields.IntField()
    score_10 = fields.IntField()

    class Meta:
        table = "bangumi_data"

    def __str__(self):
        return f"BangumiData(id={self.id}, name={self.name})"
    
BangumiData_Pydantic = pydantic_model_creator(BangumiData, name="BangumiData")
BangumiDataIn_Pydantic = pydantic_model_creator(BangumiData, name="BangumiDataIn", exclude=("id",))


class BangumiTags(models.Model):
    bangumi_id = fields.IntField()
    tag = fields.CharField(max_length=255)

    class Meta:
        table = "bangumi_tags"

    def __str__(self):
        return f"BangumiTags(bangumi_id={self.bangumi_id}, tag={self.tag})"
    
BangumiTags_Pydantic = pydantic_model_creator(BangumiTags, name="BangumiTags")
BangumiTagsIn_Pydantic = pydantic_model_creator(BangumiTags, name="BangumiTagsIn", exclude=("bangumi_id",))