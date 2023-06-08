from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser
from .permissions import CustomPermission
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    filter_backends = [DjangoFilterBackend]
    search_fields = ['username']
    permission_classes = [CustomPermission]

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)

        subscriptions = user.subscriptions.all()
        serializer = UserSerializer(subscriptions,
                                    context={'request': request}, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, pk=None):
        target_user = self.get_object()
        current_user = request.user

        if not current_user.is_authenticated:
            return Response({'detail': 'Вы не авторизованы!'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'POST':

            if current_user == target_user:
                return Response(
                    {'detail': 'Вы не можете подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST)

            if current_user.subscriptions.filter(id=target_user.id).exists():
                return Response(
                    {'detail': 'Пользователь уже добавлен в подписки!'},
                    status=status.HTTP_400_BAD_REQUEST)

            current_user.subscriptions.add(target_user)

            return Response({'detail': 'Подписка выполнена успешно!'},
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':

            if not current_user.is_authenticated:
                return Response({'detail': 'Вы не авторизованы!'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if current_user.subscriptions.filter(id=target_user.id).exists():
                current_user.subscriptions.remove(target_user)
                return Response({'detail': 'Подписка успешно удалена!'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'detail': 'Пользователь не найден в подписках!'},
                    status=status.HTTP_404_NOT_FOUND)
