import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, data = data.split(';base64,')
            extension = header.split('/')[-1]
            decoded_data = base64.b64decode(data)
            file_name = self.context['request'].user.username + '-' + str(
                uuid.uuid4())[:8] + '.' + extension
            my_file = ContentFile(decoded_data, name=file_name)
            return my_file
        return super().to_internal_value(data)
