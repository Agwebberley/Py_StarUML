# **Py_StarUML**
## **Django Model Generator from StarUML JSON**

Welcome to the documentation for **Py_StarUML**. This tool automates the creation of Django `models.py`, `views.py`, and `urls.py` files by parsing JSON exports from StarUML. It streamlines the initial setup of Django applications based on ERD diagrams, saving you time and reducing the likelihood of manual errors.

## **Table of Contents**

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Example](#example)
- [Generated Files](#generated-files)
  - [`models.py`](#modelspy)
  - [`views.py`](#viewspy)
  - [`urls.py`](#urlspy)
- [Configuration](#configuration)
- [Logging](#logging)
- [Contributing](#contributing)

---

## **Introduction**

**Py_StarUML ** is a Python script designed to automate the creation of Django models and associated views and URLs. By parsing the JSON output of StarUML ERD diagrams, it generates:

- `models.py`: Django models corresponding to your database entities.
- `views.py`: Standard CRUD views for each model using base views.
- `urls.py`: URL patterns for the generated views.

This tool is especially useful when starting new projects or when needing to quickly scaffold applications based on existing database designs.

---

## **Features**

- **Automated Model Generation**: Converts ERD entities into Django models with fields and relationships.
- **View and URL Generation**: Creates `views.py` and `urls.py` with standard CRUD operations for each model.
- **Cross-App Relationship Handling**: Manages foreign key relationships across different Django apps.
- **Customizable Logging**: Adjustable logging levels to aid in debugging and monitoring.
- **Extensible Templates**: Easy to modify the templates for `views.py` and `urls.py` to fit your project's needs.

---

## **Installation**

1. **Clone the Repository**

   ```bash
   git clone https://github.com/agwebberley/Py_StarUML.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd Py_StarUML
   ```

3. **Install Dependencies**

   The script primarily relies on Python's standard library. Ensure you have Python 3.6 or higher installed.

   ```bash
   python --version
   ```

   If additional packages are required, install them using:

   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

The script is executed from the command line and requires the path to the StarUML JSON file. Optional arguments allow you to specify the output directory and logging level.

### **Command-Line Arguments**

- **`json_file`**: Path to the JSON file containing the StarUML output. *(Required)*
- **`--output_dir`**: Directory to output the `models.py`, `views.py`, and `urls.py` files. *(Default: Current directory)*
- **`--log-level`**: Set the logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). *(Default: `WARNING`)*

### **Example**

```bash
python main.py path/to/your/staruml_output.json --output_dir ./generated_apps --log-level INFO
```

This command will:

- Parse the StarUML JSON file at `path/to/your/staruml_output.json`.
- Generate the Django files in the `./generated_apps` directory.
- Set the logging level to `INFO` to display informational messages.

---

## **Generated Files**

The script generates three key files for each app detected in the JSON data: `models.py`, `views.py`, and `urls.py`. Here's what each file contains:

### **`models.py`**

Defines Django models based on the entities and relationships from the ERD diagram.

- **Fields**: Converted from columns in the ERD, including data types and constraints.
- **Relationships**: Foreign keys are added based on the relationships in the ERD.
- **Example**:

  ```python
  from django.db import models

  class Customer(models.Model):
      id = models.AutoField(primary_key=True)
      name = models.CharField(max_length=255, null=False)
      email = models.CharField(max_length=255, null=False)
      # Additional fields...
  ```

### **`views.py`**

Provides standard CRUD views for each model using base views.

- **Imports** necessary base views and the model.
- **Class-Based Views**: `CreateView`, `ListView`, `UpdateView`, and `DeleteView`.
- **Example**:

  ```python
  from django.shortcuts import render
  from frame.base_views import (
      BaseCreateView,
      BaseListView,
      BaseUpdateView,
      BaseDeleteView,
      BaseDetailView,
  )
  from .models import Customer
  from django.urls import reverse_lazy

  class CustomerCreateView(BaseCreateView):
      model = Customer

  class CustomerListView(BaseListView):
      model = Customer

  class CustomerUpdateView(BaseUpdateView):
      model = Customer
      success_url = reverse_lazy('customers-list')

  class CustomerDeleteView(BaseDeleteView):
      model = Customer
      success_url = reverse_lazy('customers-list')
  ```

### **`urls.py`**

Defines URL patterns for the views generated in `views.py`.

- **Imports** the necessary views.
- **URL Patterns**: Paths for create, list, update, and delete operations.
- **Example**:

  ```python
  from django.urls import path
  from .views import (
      CustomerCreateView,
      CustomerListView,
      CustomerUpdateView,
      CustomerDeleteView,
  )

  urlpatterns = [
      path('create/', CustomerCreateView.as_view(), name='customers-create'),
      path('list/', CustomerListView.as_view(), name='customers-list'),
      path('update/<int:pk>/', CustomerUpdateView.as_view(), name='customers-update'),
      path('delete/<int:pk>/', CustomerDeleteView.as_view(), name='customers-delete'),
  ]
  ```

---

## **Configuration**

### **Adjusting Templates**

If you need to customize the templates for `views.py` or `urls.py`, you can modify the corresponding sections in the script.

- **Views Template**: Located in the `# Generate views.py` section.
- **URLs Template**: Located in the `# Generate urls.py` section.

### **Pluralization**

The script currently adds an "s" to model names to create plural forms. For irregular plurals, you may need to adjust the pluralization logic in the script.

### **Success URLs**

Ensure that the `success_url` in the views matches the URL names in your `urls.py`. Adjust the `success_url` if your URL patterns differ.

---

## **Logging**

The script uses Python's `logging` module to provide feedback during execution.

- **Logging Levels**:
  - `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
  - `INFO`: Confirmation that things are working as expected.
  - `WARNING`: An indication that something unexpected happened.
  - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
  - `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

- **Setting the Logging Level**: Use the `--log-level` argument to set the desired level.

  ```bash
  python main.py path/to/json --log-level DEBUG
  ```

---

## **Contributing**

Contributions are welcome! If you'd like to improve the script, please follow these steps:

1. **Fork the Repository**

   ```bash
   git clone https://github.com/yourusername/django-model-generator.git
   ```

2. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**

   - Enhance functionality.
   - Fix bugs.
   - Improve documentation.

4. **Commit and Push**

   ```bash
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**

   Go to the repository on GitHub and open a new pull request.

---


## **Additional Resources**

- **Django Documentation**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **StarUML Documentation**: [http://staruml.io/](http://staruml.io/)
- **Python Logging Module**: [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)

---

## **FAQ**

### **1. What versions of Python and Django are supported?**

The script requires Python 3.6 or higher. It generates code compatible with Django 3.x. Ensure that your Django project is set up accordingly.

### **2. Can I customize the generated code templates?**

Yes, you can modify the sections in the script where the files are generated. Look for comments like `# Generate views.py` and adjust the code as needed.

### **3. How does the script handle relationships between models in different apps?**

The script manages cross-app relationships by including the app label in the foreign key references when necessary. It ensures that foreign keys point to the correct models, even across different apps.

### **4. What if my ERD includes data types not mapped in the script?**

Unmapped data types are defaulted to `CharField` with a comment indicating the unmapped type. You can extend the `map_column_to_field` function to include additional data type mappings.

---

## **Changelog**

- **v1.0.0**
  - Initial release.
  - Generates `models.py`, `views.py`, and `urls.py` from StarUML JSON output.
  - Handles cross-app model relationships.
  - Includes logging and customizable templates.

---

## **Acknowledgments**

- **Libraries Used**:
  - Python Standard Library
  - Django Framework

---

**Thank you for using the Django Model Generator from StarUML JSON!**

Feel free to contribute, report issues, or suggest enhancements.
