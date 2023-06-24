from api.serializers import SubscribeSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .models import Subscribe
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author_id = pk
        author = get_object_or_404(CustomUser, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(author,
                                             context={"request": request})
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe, user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = request.user
        if user != request.user:
            raise PermissionDenied(
                "Вы не авторизованы!.")
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if not new_password or not current_password:
            return Response({
                'error': 'Заполните поля new_password и current_password.'},
                status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(current_password):
            return Response({'error': 'Введен неправильный пароль!.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Пароль успешно обновлен!.'},
                        status=status.HTTP_200_OK)
