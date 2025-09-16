# from ninja_jwt.controller import TokenObtainPairController
from ninja_jwt.schema import TokenObtainPairInputSchema
from ninja_extra import api_controller, route
from ninja import Schema
from django.contrib.auth import authenticate
from django.http import JsonResponse
from ninja_jwt.tokens import RefreshToken


class UserSchema(Schema):
    first_name: str
    email: str


class TokenObtainPairOutSchema(Schema):
    refresh: str
    access: str
    user: UserSchema


class TokenObtainPairSchema(TokenObtainPairInputSchema):
    def output_schema(self):
        out_dict = self.get_response_schema_init_kwargs()
        out_dict.update(user=UserSchema.from_orm(self._user))
        return TokenObtainPairOutSchema(**out_dict)


class LoginInput(Schema):
    email: str
    password: str


@api_controller("/login", tags=["Auth"])
class CustomTokenObtainPairController:
    @route.post(
        "",
        response=TokenObtainPairOutSchema,
        url_name="token_obtain_pair",
    )
    def obtain_token(self, data: LoginInput):
        user = authenticate(username=data.email, password=data.password)
        if user is None or not user.is_active:
            return JsonResponse(
                {
                    "message": "Wrong credentials!",
                    "code": "wrong_credentials_error",
                },
                status=401,
            )
        refresh = RefreshToken.for_user(user)
        return TokenObtainPairOutSchema(
            refresh=str(refresh),
            access=str(refresh.access_token),
            user=UserSchema.from_orm(user),
        )
