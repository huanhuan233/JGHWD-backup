from rest_framework import viewsets
from .models import Outline
from .serializers import OutlineSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import traceback  # 建议将导入放在文件顶部

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class OutlineViewSet(viewsets.ModelViewSet):
    serializer_class = OutlineSerializer
    # 显式声明 queryset
    queryset = Outline.objects.all()

    def get_queryset(self):
        # 只返回当前登录用户的大纲
        return Outline.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        # 方法内代码需要正确缩进（4个空格）
        title = serializer.validated_data.get('title')
        # 检查重复标题时，需限定当前用户（否则会判定其他用户的同名标题为重复）
        if Outline.objects.filter(title=title, user=self.request.user).exists():
            print(f"⚠️ 已存在相同标题大纲《{title}》，跳过保存")
            traceback.print_stack()
            return  # 防止重复保存

        # 只保存一次，同时关联当前用户
        instance = serializer.save(user=self.request.user)
        print("✅ 新建 Outline，结构内容为：")
        for i, s in enumerate(instance.structure):
            print(f"段 {i}: id={s.get('id')}, title={s.get('title')}, outline={s.get('outline')}")
        print("🛑 Outline 被创建！标题:", instance.title)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print("📦 返回的大纲结构示例：")
        if response.data and isinstance(response.data, list):
            first = response.data[0]
            print("第一个大纲标题:", first.get("title"))
            if first.get("structure"):
                for i, s in enumerate(first["structure"]):
                    print(f"段 {i}: title={s.get('title')}, outline={s.get('outline')}")
        return response