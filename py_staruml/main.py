import json
import os
import logging


def map_column_to_field(column, model_names, model_apps):
    name = column["name"]
    logging.debug(f"Mapping column: {name}")
    col_type = column["type"].upper()
    length = column.get("length", 0)
    primary_key = column.get("primaryKey", False)
    foreign_key = column.get("foreignKey", False)
    null = not primary_key  # Assume primary keys cannot be null

    if foreign_key:
        # Assume the field name is 'xxx_id', and the related model is 'Xxx'
        if name.endswith("_id"):
            related_model_name = name[:-3]
        else:
            related_model_name = name

        field_name = related_model_name.lower()
        related_model_name_cap = "".join(
            word.capitalize() for word in related_model_name.split("_")
        )

        # Use lowercased model names for consistent lookup
        related_model_key = related_model_name_cap.lower()
        related_app_name = model_apps.get(related_model_key)

        if related_app_name:
            if related_app_name != model_apps.get(column["model_name"].lower()):
                # Include app label for cross-app relations
                related_model_ref = f"{related_app_name}.{related_model_name_cap}"
            else:
                related_model_ref = related_model_name_cap
            field_def = (
                f"models.ForeignKey('{related_model_ref}', on_delete=models.CASCADE)"
            )
        else:
            field_def = f"models.IntegerField(null={null})  # ForeignKey to unknown model {related_model_name_cap}"
            logging.info(
                f"Related model not found: {related_model_name_cap}, model_apps: {model_apps}"
            )
            logging.warning(f"Foreign key to unknown model: {related_model_name_cap}")
    else:
        field_name = name
        # Map types
        if col_type == "INTEGER":
            if primary_key:
                field_def = "models.AutoField(primary_key=True)"
            else:
                field_def = f"models.IntegerField(null={null})"
        elif col_type == "VARCHAR":
            max_length = int(length) if length else 255
            field_def = f"models.CharField(max_length={max_length}, null={null})"
        elif col_type == "TEXT":
            field_def = f"models.TextField(null={null})"
        elif col_type == "DECIMAL":
            field_def = (
                f"models.DecimalField(max_digits=10, decimal_places=2, null={null})"
            )
        elif col_type == "DATETIME":
            field_def = f"models.DateTimeField(null={null})"
        else:
            field_def = f"models.CharField(max_length=255, null={null})  # Unmapped type {col_type}"
            logging.warning(f"Unmapped column type: {col_type}")

    return field_name, field_def


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Django models.py, views.py, and urls.py files from StarUML JSON output."
    )
    parser.add_argument(
        "json_file", help="Path to the JSON file containing the StarUML output."
    )
    parser.add_argument(
        "--output_dir",
        default=".",
        help="Directory to output the models.py, views.py, and urls.py files.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--slug",
        default="",
        help="Slug to use for app names (e.g. 'myapp' for 'myapp.models')",
        required=True,
    )
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % args.log_level)
    logging.basicConfig(level=numeric_level)

    json_file = args.json_file
    output_dir = args.output_dir
    slug = args.slug

    logging.info(f"Opening JSON file: {json_file}")
    with open(json_file, "r") as f:
        data = json.load(f)

    # Handle nested structure if necessary
    if isinstance(data, dict):
        if "ownedElements" in data:
            data = data["ownedElements"]
        else:
            logging.error("Invalid JSON structure.")
            return

    # Flatten the data to get entities
    entities = []

    def extract_entities(elements):
        for elem in elements:
            if elem["_type"] == "ERDEntity":
                entities.append(elem)
                logging.debug(f"Found entity: {elem['name']}")
            elif "ownedElements" in elem:
                extract_entities(elem["ownedElements"])

    extract_entities(data)

    # Create sets for model names and mapping of model names to app names
    model_names = set()
    model_apps = {}
    model_info = {}

    # Mapping from entity ID to entity (app_name, model_name)
    entity_names_by_id = {}

    # First pass: Collect all model names and apps
    for entity in entities:
        full_name = entity["name"]
        logging.info(f"Processing entity: {full_name}")
        if "." in full_name:
            app_name, model_name = full_name.split(".", 1)
        elif "_" in full_name:
            parts = full_name.split("_", 1)
            if len(parts) == 2:
                app_name, model_name = parts
            else:
                app_name = full_name
                model_name = full_name
        else:
            app_name = full_name
            model_name = full_name

        app_name = app_name.lower()
        model_name_cap = "".join(word.capitalize() for word in model_name.split("_"))
        model_name_key = model_name_cap.lower()

        model_names.add(model_name_cap)
        model_apps[model_name_key] = app_name  # Map lowercased model name to app

        entity_id = entity["_id"]
        entity_names_by_id[entity_id] = (app_name, model_name_cap)

        # Store the entity for later processing
        if app_name not in model_info:
            model_info[app_name] = {}

        model_info[app_name][model_name_cap] = {
            "entity": entity,
            "fields": [],
            "relationships": entity.get("ownedElements", []),
            "_id": entity_id,
        }

    logging.info("First pass completed.")
    logging.info(f"Model names: {model_names}")
    logging.info(f"Model apps: {model_apps}")

    # Second pass: Process columns and map columns to fields
    for app_name, app_models in model_info.items():
        for model_name, model_data in app_models.items():
            entity = model_data["entity"]
            columns = entity.get("columns", [])
            fields = []

            for column in columns:
                column["model_name"] = model_name
                field_name, field_def = map_column_to_field(
                    column, model_names, model_apps
                )
                fields.append((field_name, field_def))

            model_data["fields"] = fields

    logging.info("Second pass (columns) completed.")

    # Third pass: Process relationships
    for app_models in model_info.values():
        for model in app_models.values():
            relationships = model["relationships"]
            for relationship in relationships:
                if relationship["_type"] == "ERDRelationship":
                    end1 = relationship.get("end1", {})
                    end2 = relationship.get("end2", {})
                    ref1_id = end1.get("reference", {}).get("$ref")
                    ref2_id = end2.get("reference", {}).get("$ref")
                    cardinality = end2.get("cardinality", "")

                    entity1_info = entity_names_by_id.get(ref1_id)
                    entity2_info = entity_names_by_id.get(ref2_id)

                    if not entity1_info or not entity2_info:
                        logging.warning("Relationship references unknown entities.")
                        continue

                    entity1_app, entity1_model = entity1_info
                    entity2_app, entity2_model = entity2_info

                    field_name = entity1_model.lower()
                    if entity1_app != entity2_app:
                        # Include app label for cross-app relations
                        related_model_ref = f"{entity1_app}.{entity1_model}"
                    else:
                        related_model_ref = entity1_model

                    field_def = f"models.ForeignKey('{related_model_ref}', on_delete=models.CASCADE)"

                    if cardinality in ["0..*", "1..*"]:
                        # Add ForeignKey in entity2_model pointing to entity1_model
                        model_fields = (
                            model_info.get(entity2_app, {})
                            .get(entity2_model, {})
                            .get("fields", [])
                        )
                        # Check if the field already exists
                        if field_name not in [field[0] for field in model_fields]:
                            model_fields.append((field_name, field_def))
                            model_info[entity2_app][entity2_model]["fields"] = (
                                model_fields
                            )
                            logging.debug(
                                f"Added ForeignKey from {entity2_model} to {entity1_model}"
                            )

    logging.info("Third pass (relationships) completed.")

    # Output models.py, views.py, and urls.py files per app
    for app_name, app_models in model_info.items():
        app_dir = os.path.join(output_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)

        # Touch __init__.py
        init_py_path = os.path.join(app_dir, "__init__.py")
        with open(init_py_path, "w") as f:
            f.write("# __init__.py\n")

        # Generate apps.py
        apps_py_path = os.path.join(app_dir, "apps.py")
        with open(apps_py_path, "w") as f:
            f.write("from django.apps import AppConfig\n\n")
            f.write(f"class {app_name.capitalize()}Config(AppConfig):\n")
            f.write(f"    default_auto_field = 'django.db.models.BigAutoField'\n")
            f.write(f"    name = '{slug}.{app_name}'\n")

        models_py_path = os.path.join(app_dir, "models.py")

        with open(models_py_path, "w") as f:
            f.write(
                "from django.db import models\nfrom frame.models import BaseModel\n\n"
            )
            for model_name, model_data in app_models.items():
                f.write(f"class {model_name}(BaseModel):\n")
                fields = model_data["fields"]
                if not fields:
                    f.write("    pass\n\n")
                else:
                    for field_name, field_def in fields:
                        f.write(f"    {field_name} = {field_def}\n")
                    f.write("\n")

                # Build the config dictionary
                config = {}
                config["model_name"] = model_name
                config["list_title"] = model_name + "s"  # Simple pluralization
                config["create_title"] = "Create " + model_name
                config["enable_search"] = True
                # For default_sort_by, pick 'created_at' if it exists, else the first field
                field_names = [field_name for (field_name, field_def) in fields]
                if "created_at" in field_names:
                    config["default_sort_by"] = "created_at"
                else:
                    config["default_sort_by"] = field_names[0] if field_names else ""
                config["list_url"] = model_name.lower() + "-list"
                config["navigation"] = True
                # Build fields configuration
                config_fields = []
                for field_name in field_names:
                    field_config = {
                        "name": field_name,
                        "display_name": field_name.replace("_", " ").title(),
                        "enable_in_list": True,
                        "enable_in_detail": True,
                        "enable_in_form": True,
                    }
                    config_fields.append(field_config)
                config["fields"] = config_fields

                config["actions"] = {
                    "button": [
                        {
                            "name": "Create",
                            "url": model_name.lower() + "-create",
                            "disabled": ["detail"],
                        },
                    ],
                    "dropdown": [
                        {
                            "name": "Details",
                            "url": model_name.lower() + "-detail",
                            "disabled": ["detail"],
                        },
                        {
                            "name": "Edit",
                            "url": model_name.lower() + "-update",
                        },
                        {
                            "name": "Delete",
                            "url": model_name.lower() + "-delete",
                        },
                    ],
                }

                # Write the get_config class method
                f.write("    @classmethod\n")
                f.write("    def get_config(cls):\n")
                f.write("        return ")
                # Use json.dumps for pretty-printing the dictionary
                config_str = json.dumps(config, indent=8)
                config_lines = config_str.splitlines()
                for line in config_lines:
                    # Fix true/false to True/False
                    line = line.replace("true", "True").replace("false", "False")
                    f.write("        " + line + "\n")
                f.write("\n")

        logging.info(f"Generated {models_py_path}")

        # Generate views.py
        views_py_path = os.path.join(app_dir, "views.py")
        with open(views_py_path, "w") as f:
            # Write imports
            f.write("from django.shortcuts import render\n")
            f.write("from frame.base_views import (\n")
            f.write("    BaseCreateView,\n")
            f.write("    BaseListView,\n")
            f.write("    BaseUpdateView,\n")
            f.write("    BaseDeleteView,\n")
            f.write("    BaseDetailView,\n")
            f.write(")\n")
            f.write(f"from .models import {', '.join(app_models.keys())}\n")
            f.write("from django.urls import reverse_lazy\n")
            f.write("# Create your views here.\n\n")

            # Generate views for each model
            for model_name in app_models.keys():
                model_name_lower = model_name.lower()
                # CreateView
                f.write(f"class {model_name}CreateView(BaseCreateView):\n")
                f.write(f"    model = {model_name}\n")
                f.write(
                    f"    success_url = reverse_lazy('{model_name_lower}-list')\n\n"
                )
                # ListView
                f.write(f"class {model_name}ListView(BaseListView):\n")
                f.write(f"    model = {model_name}\n\n")
                # UpdateView
                f.write(f"class {model_name}UpdateView(BaseUpdateView):\n")
                f.write(f"    model = {model_name}\n")
                f.write(
                    f"    success_url = reverse_lazy('{model_name_lower}-list')\n\n"
                )
                # DeleteView
                f.write(f"class {model_name}DeleteView(BaseDeleteView):\n")
                f.write(f"    model = {model_name}\n")
                f.write(
                    f"    success_url = reverse_lazy('{model_name_lower}-list')\n\n"
                )
                # DetailView
                f.write(f"class {model_name}DetailView(BaseDetailView):\n")
                f.write(f"    model = {model_name}\n\n")
        logging.info(f"Generated {views_py_path}")

        # Generate urls.py
        urls_py_path = os.path.join(app_dir, "urls.py")
        with open(urls_py_path, "w") as f:
            # Write imports
            f.write("from django.urls import path\n")
            f.write("from .views import (\n")
            for model_name in app_models.keys():
                f.write(f"    {model_name}CreateView,\n")
                f.write(f"    {model_name}ListView,\n")
                f.write(f"    {model_name}UpdateView,\n")
                f.write(f"    {model_name}DeleteView,\n")
                f.write(f"    {model_name}DetailView,\n")
            f.write(")\n\n")

            # Start urlpatterns
            f.write("urlpatterns = [\n")
            for model_name in app_models.keys():
                model_name_lower = model_name.lower()
                # CreateView
                f.write(
                    f"    path('{model_name_lower}/create/', {model_name}CreateView.as_view(), name='{model_name_lower}-create'),\n"
                )
                # ListView
                f.write(
                    f"    path('{model_name_lower}/list/', {model_name}ListView.as_view(), name='{model_name_lower}-list'),\n"
                )
                # UpdateView
                f.write(
                    f"    path('{model_name_lower}/update/<int:pk>/', {model_name}UpdateView.as_view(), name='{model_name_lower}-update'),\n"
                )
                # DeleteView
                f.write(
                    f"    path('{model_name_lower}/delete/<int:pk>/', {model_name}DeleteView.as_view(), name='{model_name_lower}-delete'),\n"
                )
                # DetailView
                f.write(
                    f"    path('{model_name_lower}/detail/<int:pk>/', {model_name}DetailView.as_view(), name='{model_name_lower}-detail'),\n"
                )
            f.write("]\n")
        logging.info(f"Generated {urls_py_path}")

    logging.info("models.py, views.py, and urls.py files generated successfully.")


if __name__ == "__main__":
    main()
