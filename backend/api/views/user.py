from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from ..mixins import SubscriptionMixin
from ..serializers.user import (CustomUserSerializer, SetAvatarSerializer,
                                SubscriptionCreateSerializer,
                                SubscriptionSerializer)


class CustomUserViewSet(SubscriptionMixin, UserViewSet):
    """Extended user viewset with subscription and avatar management.

    Provides endpoints for user profile management with the following permissions:
        - Guests can view user profiles (list, retrieve)
        - Users can manage their own profile
        - Users can manage their subscriptions
        - Users can manage their avatar

    Attributes:
        queryset: QuerySet of all users
        serializer_class: Default serializer for user operations
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
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_with_count = User.objects.annotate(
                recipes_count=Count('recipes')
            ).get(id=author.id)
            return Response(
                SubscriptionSerializer(
                    author_with_count,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if not subscription.exists():
            return Response(
                {'errors': 'You are not subscribed to this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).annotate(
            recipes_count=Count('recipes')
        )
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
            if request.user.avatar:
                request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 