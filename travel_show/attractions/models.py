from django.db import models


class Attraction(models.Model):
    id = models.CharField(primary_key=True, max_length=50, db_comment='高德POI唯一ID')
    name = models.CharField(max_length=200, db_comment='景点名称')
    city = models.CharField(max_length=100, blank=True, null=True, db_comment='城市')
    province = models.CharField(max_length=50, blank=True, null=True, db_comment='省份')
    adcode = models.CharField(max_length=20, blank=True, null=True, db_comment='行政区划代码')
    location = models.CharField(max_length=50, blank=True, null=True, db_comment='经纬度')
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, db_comment='评分')
    type = models.CharField(max_length=200, blank=True, null=True, db_comment='分类')
    address = models.CharField(max_length=300, blank=True, null=True, db_comment='详细地址')
    tel = models.CharField(max_length=50, blank=True, null=True, db_comment='电话')
    opentime = models.TextField(blank=True, null=True, db_comment='开放时间')
    photos = models.TextField(blank=True, null=True, db_comment='图片URL列表(JSON)')
    keytag = models.CharField(max_length=100, blank=True, null=True, db_comment='特色标签')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attractions'

    def __str__(self):
        return self.name


from django.db import models

# Create your models here.
