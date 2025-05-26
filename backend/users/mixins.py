from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Subscription
from .serializers import SubscriptionSerializer


class SubscriptionMixin:
    def handle_subscription(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'You cannot subscribe to yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'You are already subscribed to this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if not subscription.exists():
                return Response(
                    {'errors': 'You are not subscribed to this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 