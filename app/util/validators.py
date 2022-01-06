register_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "username": {
            "type": "string",
        },
        "password": {"type": "string", "minLength": 10},
    },
    "required": ["name", "surname", "email", "username", "password"],
}

login_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"},
    },
    "required": ["email", "password"],
}

reserve_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "places": {"type": "integer"},
    },
    "required": ["id", "places"],
}

request_new_role_schema = {
    "type": "object",
    "properties": {"role_type": {"type": "string"}},
    "required": ["role_type"],
}
