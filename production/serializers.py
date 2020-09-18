from rest_framework import serializers
from .models import UserProfile, Productions

class UserProfileSerializers(serializers.ModelSerializer):

    def create(self, validated_data):
        user = super(UserProfileSerializers, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.is_active = True
        user.save()
        return user

    class Meta:
        model = UserProfile
        fields = "__all__"

class UserDetailSerializers(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"


class ProductionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Productions
        fields = "__all__"

