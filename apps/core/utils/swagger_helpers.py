from rest_framework import serializers


def create_response_serializer(data_serializer_class, many=False):
    """
    Creates a response serializer with the standard API format
    """
    # Create unique class name to avoid conflicts
    base_name = getattr(data_serializer_class, '__name__', 'Data')
    class_name = f"{base_name}Response{'List' if many else 'Detail'}"

    # Define attributes dynamically
    attrs = {
        'message': serializers.CharField(default="success"),
        'status': serializers.BooleanField(default=True),
        'data': data_serializer_class(many=many)
    }

    # Create the class dynamically with proper naming
    ResponseSerializer = type(class_name, (serializers.Serializer,), attrs)
    return ResponseSerializer
