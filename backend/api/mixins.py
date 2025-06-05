from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .serializers.user import (SubscriptionCreateSerializer,
                               SubscriptionSerializer)


class SubscriptionMixin:
    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def subscribe(self, request, id=None):
        user = request.user

        if request.method == 'POST':
            author = get_object_or_404(User, id=id)
            serializer = SubscriptionCreateSerializer(
                data={'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count = Subscription.objects.filter(
            user=user,
            author_id=id
        ).delete()[0]
        if not deleted_count:
            return Response(
                {'errors': 'You are not subscribed to this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get']
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)