from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from djoser.views import UserViewSet
from .models import User, Subscription
from .serializers import (
    CustomUserSerializer,
    SubscriptionSerializer,
    SetAvatarSerializer
)
from .mixins import SubscriptionMixin


class CustomUserViewSet(SubscriptionMixin, UserViewSet):
    """
    User viewset with the following permissions:
    - Guests can view user profiles
    - Users can manage their own profile
    - Users can manage their subscriptions
    - Users can manage their avatar
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        return self.handle_subscription(request, id)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribing__user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='user-avatar'
    )
    def me_avatar(self, request):
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                request.user,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == 'DELETE':
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT) 