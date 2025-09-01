from ninja_jwt.schema import TokenObtainPairInputSchema
from ninja_jwt.controller import TokenObtainPairController
from ninja_extra import api_controller, route
from ninja import Schema


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


@api_controller(
    "/login", tags=["Auth"]
)  # Custom path as in your previous setup
class CustomTokenObtainPairController(TokenObtainPairController):
    @route.post(
        "",
        response=TokenObtainPairOutSchema,
        url_name="token_obtain_pair",
    )
    def obtain_token(self, user_token: TokenObtainPairSchema):
        return user_token.output_schema()
