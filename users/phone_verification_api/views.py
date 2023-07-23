from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .serializers import CustomPhoneVerificationSerializer
from phone_verify.api import VerificationViewSet
from phone_verify.base import response
from phone_verify.serializers import PhoneSerializer, SMSVerificationSerializer
from phone_verify.services import send_security_code_and_generate_session_token

view_response = openapi.Response(description='response description', examples={"application/json": {
    "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpb3NfKzkxOTkxMTcxNTkyOV9zZXNzaW9uX2NvZGUiOiI3MTExNDYifQ.XSIBOsfA6kYd8NUE2MlvhdrOZszoWQdzunOGEU_Wr94"
}})


class CustomPhoneVerificationViewSet(VerificationViewSet):
    @swagger_auto_schema(responses={200: view_response})
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
