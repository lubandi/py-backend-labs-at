from drf_spectacular.extensions import OpenApiAuthenticationExtension


class MicroserviceTokenScheme(OpenApiAuthenticationExtension):
    target_class = "extractor.permissions.MicroserviceTokenAuthentication"
    name = "MicroserviceToken"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-Microservice-Token",
            "description": "Token for microservice-to-microservice communication.",
        }
