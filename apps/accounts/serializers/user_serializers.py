from rest_framework import serializers

from apps.accounts.models import Role, User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_active", "created_at"]
        read_only_fields = fields

    def get_role(self, obj):
        return obj.role_name


class UserUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[Role.VIEWER, Role.ANALYST, Role.ADMIN], required=False)
    is_active = serializers.BooleanField(required=False)
