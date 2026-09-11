from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from users.business.services import UserService
from users.presentation.serializers import UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class UserView(View):
    serializer_class = UserSerializer
    service_class = UserService

    def get(self, request: HttpRequest) -> JsonResponse:
        users = self.service_class().list_users()
        return JsonResponse({"users": self.serializer_class().dump_many(users)})

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            payload = json.loads(request.body or b"{}")
            data = self.serializer_class().load(payload)
            user = self.service_class().register_user(**data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON invalide."}, status=400)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        return JsonResponse(self.serializer_class().dump(user), status=201)
