# ansible-inventory-utils

Tool for manipulating data defined in the inventory file of [Ansible](https://github.com/ansible/ansible).

## Installation

`pip install -r requirements.txt`

## Usage

```Python
from ansibleutils import load_ansible_inventory, diff_ansible_inventory

# Load ansible inventory
inventory = load_ansible_inventory("path/to/ansible/base_dir", "path/to/ansible/inventory", "VaultPassword")

# Check if two ansible inventories are the same
new_inventory = load_ansible_inventory("path/to/ansible/base_dir", "path/to/ansible/new_inventory", "VaultPassword")
if diff_ansible_inventory(inventory, new_inventory, debug=True):
    print("two inventories are the same")
else:
    print("two inventories are different")
```

## Requirements
- ansible 2.1.0

