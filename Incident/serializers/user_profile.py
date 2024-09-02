from rest_framework import serializers
from Incident.models import CustomUser
import re
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes
from django.utils.http import urlsafe_base64_encode
from Incident.utils import Utils
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from localflavor.in_.models import INStateField
from django_countries.fields import CountryField
from django_countries import countries




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_isd_code',
            'phone_number',
            'address',
            'pin_code',
            'city',
            'country',
            'fax_number',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'password', 'confirm_password', 
            'phone_number', 'phone_isd_code', 'fax_number', 'address', 'pin_code',
            'city', 'state', 'country',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': True},
            'phone_isd_code': {'required': True},
            'address': {'required': True},
            'pin_code': {'required': True},
            'city': {'required': True},
            'state': {'required': True},
            'country': {'required': True},
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Password and Confirm Password must be the same."})

        if not re.match(pattern, password):
            raise serializers.ValidationError({"password": "Password must contain at least eight characters with a digit, an uppercase letter, and a lowercase letter."})
        
        return attrs

    def create(self, validated_data):
        user = CustomUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            phone_isd_code=validated_data.get('phone_isd_code', '+91'),
            address=validated_data['address'],
            pin_code=validated_data['pin_code'],
            city=validated_data['city'],
            state=validated_data['state'],
            country=validated_data['country'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("The old password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("The new password and confirm new passwords do not match.")
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f'http://127.0.0.1:3000/password-reset/{uid}/{token}'
            print(link)
            # Send Email
            body = f'Click the following link to reset your password: {link}'
            data = {
                'email_subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Utils.send_email(data)
            return attrs
        else:
            raise ValidationError('You are not a registered user')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        uid = self.context.get('uid')
        token = self.context.get('token')

        if password != confirm_password:
            raise serializers.ValidationError("Password and Confirm Password don't match.")

        try:
            id = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError('Token is not valid or expired')
            user.set_password(password)
            user.save()
            return attrs
        except (CustomUser.DoesNotExist, UnicodeDecodeError):
            raise ValidationError('Token is not valid or expired')




