from phone_verify.serializers import PhoneSerializer
from ..custom_funcs import validate_phone


class CustomPhoneVerificationSerializer(PhoneSerializer):

    def validate(self, attrs):
        if "phone" in attrs:
            phone = validate_phone(attrs["phone"])
            if phone[0] == "0":
                phone = "+996" + phone[1:]
            attrs["phone"] = phone
        return super(CustomPhoneVerificationSerializer, self).validate(attrs)
