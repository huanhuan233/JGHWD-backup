from django.db import models
from django.conf import settings 
class KnowledgeConfig(models.Model):
    name = models.CharField(max_length=100)       # 配置名称（用户起的）
    type = models.CharField(max_length=50)        # 知识库类型，例如 dify
    api_key = models.TextField()                  # Dify 提供的 API Key
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
def __str__(self):
    return f"{self.name} ({self.type})"
