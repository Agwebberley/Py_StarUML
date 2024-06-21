import json

json_schema = """
{
  "orders": {
    "order": {
      "columns": [
        {"customer_id": ["INTEGER", 0, false, false, false]},
        {"order_date": ["DATETIME", 0, false, false, false]},
        {"total_amount": ["DECIMAL", 0, false, false, false]},
        {"status": ["VARCHAR", 255, false, false, false]},
        {"created_at": ["DATETIME", 0, false, false, false]},
        {"updated_at": ["DATETIME", 0, false, false, false]}
      ],
      "relationships": []
    },
    "order_item": {
      "columns": [
        {"quantity": ["INTEGER", 0, false, false, false]},
        {"unit_price": ["DECIMAL", 0, false, false, false]},
        {"created_at": ["DATETIME", 0, false, false, false]},
        {"updated_at": ["DATETIME", 0, false, false, false]}
      ],
      "relationships": [
        {"order_id": ["orders", "order", "0..*"]},
        {"part_id": ["inventory", "part", "0..*"]}
      ]
    }
  },
  "customers": {
    "customer": {
      "columns": [
        {"name": ["VARCHAR", 255, false, false, false]},
        {"email": ["VARCHAR", 255, false, false, false]},
        {"phone": ["INTEGER", 0, false, false, false]},
        {"created_at": ["DATETIME", 0, false, false, false]},
        {"updated_at": ["DATETIME", 0, false, false, false]}
      ],
      "relationships": []
    }
  },
  "inventory": {
    "part": {
      "columns": [
        {"name": ["VARCHAR", 255, false, false, false]},
        {"description": ["TEXT", 255, false, false, false]},
        {"price": ["DECIMAL", 0, false, false, false]},
        {"stock_quantity": ["INTEGER", 0, false, false, false]},
        {"created_at": ["DATETIME", 0, false, false, false]},
        {"updated_at": ["DATETIME", 0, false, false, false]}
      ],
      "relationships": []
    }
  }
}
"""

data_types = {
    "INTEGER": "models.IntegerField()",
    "VARCHAR": "models.CharField(max_length={})",
    "DATETIME": "models.DateTimeField()",
    "DECIMAL": "models.DecimalField(max_digits=10, decimal_places=2)",
    "TEXT": "models.TextField()"
}

relationship_types = {
    "0..*": "models.ForeignKey('{}', on_delete=models.CASCADE)",
    "1..*": "models.ForeignKey('{}', on_delete=models.CASCADE)",
    "0..1": "models.OneToOneField('{}', on_delete=models.CASCADE)",
    "1..1": "models.OneToOneField('{}', on_delete=models.CASCADE)"
}

def generate_django_model(model_name, columns, relationships):
    model_str = f"class {model_name.capitalize()}(models.Model):\n"
    for column in columns:
        for name, props in column.items():
            field_type = props[0]
            if field_type in data_types:
                if field_type == "VARCHAR":
                    model_str += f"    {name} = {data_types[field_type].format(props[1])}\n"
                else:
                    model_str += f"    {name} = {data_types[field_type]}\n"
    for relationship in relationships:
        for field, rel_props in relationship.items():
            related_app = rel_props[0]
            related_model = rel_props[1]
            rel_type = rel_props[2]
            if rel_type in relationship_types:
                model_str += f"    {field} = {relationship_types[rel_type].format(related_model.capitalize())}\n"
    model_str += "\n"
    return model_str

def generate_graphene_type(model_name, columns, relationships):
    type_str = f"class {model_name.capitalize()}Type(DjangoObjectType):\n"
    type_str += "    class Meta:\n"
    type_str += f"        model = {model_name.capitalize()}\n"
    type_str += "\n"
    return type_str

def generate_graphene_query(model_name):
    query_str = f"    all_{model_name}s = graphene.List({model_name.capitalize()}Type)\n\n"
    query_str += f"    def resolve_all_{model_name}s(self, info, **kwargs):\n"
    query_str += f"        return {model_name.capitalize()}.objects.all()\n\n"
    return query_str

schema = json.loads(json_schema)
django_models = ""
graphene_types = ""
graphene_queries = "class Query(graphene.ObjectType):\n"
imports = {
    "django_models": "from django.db import models\n",
    "graphene_types": "import graphene\nfrom graphene_django.types import DjangoObjectType\n"
}

for app_name, models in schema.items():
    django_models += f"\n# Models for {app_name.capitalize()} app\n"
    graphene_types += f"\n# GraphQL Types for {app_name.capitalize()} app\n"
    for model_name, model_data in models.items():
        columns = model_data["columns"]
        relationships = model_data["relationships"]

        # Generate Django models
        django_models += generate_django_model(model_name, columns, relationships)

        # Generate Graphene types
        graphene_types += generate_graphene_type(model_name, columns, relationships)

        # Generate Graphene queries
        graphene_queries += generate_graphene_query(model_name)

# Output the generated code
print("Django Models:\n")
print(imports["django_models"])
print(django_models)

print("\nGraphene Types:\n")
print(imports["graphene_types"])
print(graphene_types)

print("\nGraphene Query:\n")
print(graphene_queries)
