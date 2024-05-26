# Create Django project
django-admin startproject webhook_project
cd webhook_project

python manage.py startapp webhook
from django.db import models

class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.CharField(unique=True, max_length=100)
    account_name = models.CharField(max_length=100)
    app_secret_token = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.account_name

class Destination(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    url = models.URLField()
    http_method = models.CharField(max_length=10)
    headers = models.JSONField()

    def __str__(self):
        return self.url

    from rest_framework import serializers
    from .models import Account, Destination

    class AccountSerializer(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = '__all__'

    class DestinationSerializer(serializers.ModelSerializer):
        class Meta:
            model = Destination
            fields = '__all__'

    from rest_framework import viewsets
    from .models import Account, Destination
    from .serializers import AccountSerializer, DestinationSerializer

    class AccountViewSet(viewsets.ModelViewSet):
        queryset = Account.objects.all()
        serializer_class = AccountSerializer

    class DestinationViewSet(viewsets.ModelViewSet):
        queryset = Destination.objects.all()
        serializer_class = DestinationSerializer
        from django.urls import path, include
        from rest_framework.routers import DefaultRouter
        from .views import AccountViewSet, DestinationViewSet

        router = DefaultRouter()
        router.register(r'accounts', AccountViewSet)
        router.register(r'destinations', DestinationViewSet)

        urlpatterns = [
            path('', include(router.urls)),
        ]
        import uuid
        from django.db import models

        class Account(models.Model):
            # Other fields...

            def save(self, *args, **kwargs):
                if not self.app_secret_token:
                    self.app_secret_token = uuid.uuid4().hex
                super().save(*args, **kwargs)

            from django.http import JsonResponse
            from django.views.decorators.csrf import csrf_exempt
            import requests

            @csrf_exempt
            def webhook_receiver(request, account_id):
                if request.method == 'POST':
                    data = request.POST.dict()
                    account = Account.objects.get(account_id=account_id)
                    destinations = Destination.objects.filter(account=account)
                    for destination in destinations:
                        headers = destination.headers
                        response = requests.request(
                            method=destination.http_method,
                            url=destination.url,
                            headers=headers,
                            json=data
                        )
                        # Handle response if needed
                    return JsonResponse({'message': 'Webhook received and sent to destinations.'})
                    from django.urls import path
                    from .views import webhook_receiver

                    urlpatterns = [
                        path('webhook/<str:account_id>/', webhook_receiver),
                    ]
