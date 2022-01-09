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
        "username": {"type": "string"},
        "password": {"type": "string"},
    },
    "required": ["username", "password"],
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

create_arrangement_schema = {
    "type": "object",
    "properties": {
        "available_seats": {"type": "integer"},
        "description": {"type": "string"},
        "destination": {"type": "string"},
        "end_date": {"type": "string"},
        "price": {"type": "integer"},
        "start_date": {"type": "string"},
    },
    "required": [
        "available_seats",
        "description",
        "destination",
        "end_date",
        "price",
        "start_date",
    ],
}

role_change_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["approved", "denied"]},
        "comment": {"type": "string"},
    },
    "required": ["action"],
}

date_time_format = "%d %b %Y %H:%M"
