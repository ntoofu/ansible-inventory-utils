"""
This module defines utilities to handle ansible inventory
"""

def load_ansible_inventory(base_dir, inventory_file, vault_pass=None):
    """
    Args:
        base_dir       (str): path for Ansible base directory
        inventory_file (str): path for Ansible inventory file
        vault_pass     (str, optional): Vault password
    Returns:
        ansible.inventory.Inventory: Ansible inventory object
    """
    from ansible.inventory import Inventory
    from ansible.vars import VariableManager
    from ansible.parsing.dataloader import DataLoader

    variable_manager = VariableManager()
    loader = DataLoader()
    if vault_pass:
        loader.set_vault_password(vault_pass)
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory_file)
    inventory.set_playbook_basedir(base_dir)
    variable_manager.set_inventory(inventory)

    return inventory

def diff_ansible_inventory(inventory1, inventory2, debug=False):
    """
    Args:
        inventory1 (ansible.inventory.Inventory): Ansible inventory compared to the latter one.
        inventory2 (ansible.inventory.Inventory): Ansible inventory compared to the former one.
        debug (bool, optional): Output debug information if True
    Returns:
        bool: True if contents of the given inventories are the same, False otherwise.
    """
    comparison = AnsibleComparator(inventory1, inventory2)
    if debug and comparison.result != BaseComparator.eq:
        print("position: {}\ndifference: {}".format(" -> ".join(comparison.path), comparison.diff))
    return comparison.result == BaseComparator.eq

class BaseComparator():
    (lt, eq, gt) = (-1, 0, 1)

    def __init__(self, obj1, obj2):
        self._obj1 = obj1
        self._obj2 = obj2
        self.path = []
        self.diff = ()
        self.result = 0
        self._compare()

    def _compare(self):
        pass

    def recurse_compare(self, comparator):
        self.result = comparator.result
        self.diff = comparator.diff
        if comparator.result != self.eq:
            self.path.extend(comparator.path)
        return True if self.result == self.eq else False

class AnsibleComparator(BaseComparator):
    """
    Class to compare Ansible inventories.

    Args:
        inventory1 (ansible.inventory.Inventory): Ansible inventory compared to the latter one
        inventory2 (ansible.inventory.Inventory): Ansible inventory compared to the former one
    Attributes:
        result(bool)
        diff(str)
    """

    def _compare(self):
        i1 = self._obj1
        i2 = self._obj2
        if self.recurse_compare(ListComparator(GroupComparator, i1.groups.values(), i2.groups.values())) is False:
            return
        self.result = self.eq


class ListComparator(BaseComparator):
    def __init__(self, comparator, *args, **kwargs):
        self._elem_cmp = comparator
        super(ListComparator, self).__init__(*args, **kwargs)

    def _compare(self):
        l1 = self._obj1
        l2 = self._obj2
        if len(l1) != len(l2):
            self.diff = (l1, l2)
            self.path = ["list"]
            if len(l1) < len(l2):
                self.result = self.lt
            else:
                self.result = self.gt
            return
        sorted1 = sorted(l1, key=self._cmp_to_key(lambda x,y: self._elem_cmp(x,y).result))
        sorted2 = sorted(l2, key=self._cmp_to_key(lambda x,y: self._elem_cmp(x,y).result))
        for i in range(0,len(sorted1)):
            if self.recurse_compare(self._elem_cmp(sorted1[i], sorted2[i])) is False:
                return
        self.result = self.eq
        return

    @staticmethod
    def _cmp_to_key(mycmp):
         'Convert a cmp= function into a key= function'
         class K:
             def __init__(self, obj, *args):
                 self.obj = obj
             def __lt__(self, other):
                 return mycmp(self.obj, other.obj) < 0
             def __gt__(self, other):
                 return mycmp(self.obj, other.obj) > 0
             def __eq__(self, other):
                 return mycmp(self.obj, other.obj) == 0
             def __le__(self, other):
                 return mycmp(self.obj, other.obj) <= 0
             def __ge__(self, other):
                 return mycmp(self.obj, other.obj) >= 0
             def __ne__(self, other):
                 return mycmp(self.obj, other.obj) != 0
         return K


class GroupComparator(BaseComparator):
    def _compare(self):
        g1 = self._obj1
        g2 = self._obj2
        if g1.name != g2.name:
            self.diff = (g1.name,g2.name)
            self.path = ["name"]
            if g1.name < g2.name:
                self.result = self.lt
            else:
                self.result = self.gt
            return
        self.path = [g1.name]

        if self.recurse_compare(VarsComparator(dict(g1.vars), dict(g2.vars))) is False:
            return

        if self.recurse_compare(ListComparator(HostComparator, g1.hosts, g2.hosts)) is False:
            return

        if self.recurse_compare(ListComparator(HostComparator, g1.child_groups, g2.child_groups)) is False:
            return
        self.result = self.eq
        return

class HostComparator(BaseComparator):
    def _compare(self):
        h1 = self._obj1
        h2 = self._obj2
        if h1.name != h2.name:
            self.diff = (h1.name,h2.name)
            self.path = ["name"]
            if h1.name < h2.name:
                self.result = self.lt
            else:
                self.result = self.gt
            return
        self.path = [h1.name]
        self.recurse_compare(VarsComparator(dict(h1.vars), dict(h2.vars)))
        return

class VarsComparator(BaseComparator):
    def _compare(self):
        d1 = self._obj1
        d2 = self._obj2
        if d1 == d2:
            self.result = self.eq
        else:
            self.diff = (d1, d2)
            self.path = ["vars"]
            if str(d1) < str(d2):
                self.result = self.lt
            else:
                self.result = self.gt
        return

