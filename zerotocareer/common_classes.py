from rest_framework_swagger import renderers


class JSONOpenAPIRender(renderers.OpenAPIRenderer):
	media_type = 'application/json'
