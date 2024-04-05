import os

host = os.environ.get("SWAGGER_HOST")
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Tller API Docs",
        "description": "API Documentation for Tiller Application",
        "contact": {
            "name": "Admin",
            "email": "antonygichoya9@gmail.com",
            "url": "https://tiller.onrender.com",
        },
        "termsOfService": "Terms of services",
        "version": "1.0",
        "license": {
            "name": "License of API",
            "url": "https://github.com/KariukiAntony",
        },
    },
    "basePath": "/api/v1",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using "
            + 'the Bearer scheme.Example "Bearer {token}"',
        },
    },
    # "security": [{"Bearer": []}], # secures all the endpints
}

swagger_config = {
    "headers": [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE"),
    ],
    "specs": [
        {
            "endpoint": "/apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",  # url of the swagger ui
}
