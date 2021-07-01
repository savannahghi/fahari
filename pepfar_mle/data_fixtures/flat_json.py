from django.core.serializers.json import Serializer as DjangoJsonSerializer


class Serializer(DjangoJsonSerializer):
    def get_dump_object(self, obj):
        data = super(Serializer, self).get_dump_object(obj)
        data.update(data.pop("fields", {}))
        data["id"] = data.pop("pk")
        return data

    def handle_fk_field(self, obj, field):
        super(Serializer, self).handle_fk_field(obj, field)
        value = self._current.pop(field.name)
        if value:
            self._current[field.name] = {"id": value}
