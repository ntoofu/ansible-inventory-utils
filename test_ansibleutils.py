import unittest, sys
from ansibleutils import load_ansible_inventory, diff_ansible_inventory

class AnsibleComparatorTestCase(unittest.TestCase):
    def setUp(self):
        self.inventory_config = [
                {
                    "base_dir": "testdata/1/",
                    "inventory_file": "testdata/1/inventory",
                    "vault_pass": ""
                    },
                {
                    "base_dir": "testdata/2/",
                    "inventory_file": "testdata/2/inventory",
                    "vault_pass": ""
                    },
                {
                    "base_dir": "testdata/3/",
                    "inventory_file": "testdata/3/inventory",
                    "vault_pass": ""
                    },
                {
                    "base_dir": "testdata/4/",
                    "inventory_file": "testdata/4/inventory",
                    "vault_pass": "VaultPassword"
                    }
                ]
        self.inventory = [load_ansible_inventory(config["base_dir"], config["inventory_file"], config["vault_pass"]) for config in self.inventory_config]

    def test_same_inventories(self):
        results = []
        for inventory in self.inventory:
            results.append(diff_ansible_inventory(inventory, inventory, True))
        self.assertFalse(False in results)

    def test_different_inventories(self):
        different_index_pairs = [ (x,y) for x in range (0, len(self.inventory)) for y in range (0, len(self.inventory)) if x<y ]
        results = []
        for index_pair in different_index_pairs:
            inventory1 = self.inventory[index_pair[0]]
            inventory2 = self.inventory[index_pair[1]]
            results.append(diff_ansible_inventory(inventory1, inventory2, True))
        self.assertFalse(True in results)

if __name__ == '__main__':
     unittest.main()
