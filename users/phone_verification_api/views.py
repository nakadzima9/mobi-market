from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .serializers import CustomPhoneVerificationSerializer
from phone_verify.api import VerificationViewSet
from phone_verify.base import response
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from phone_verify.services import send_security_code_and_generate_session_token


class CustomPhoneVerificationViewSet(VerificationViewSet):
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=CustomPhoneVerificationSerializer,
    )
    def register(self, request):
        serializer = CustomPhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_token": session_token})