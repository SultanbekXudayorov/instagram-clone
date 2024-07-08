import datetime
from django.forms import ValidationError
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import SignUpSerializers
from .models import CODE_VERIFIED, DONE, NEW, User
from rest_framework.generics import CreateAPIView

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializers



class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)

        return Response(
            data={
                "success":"True",
                "auth_status": user.auth_status,
                "access":  user.token()['access'],
                "refresh": user.token()['refresh'],
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }

            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True
