import json
import os
import subprocess

class Module:
    """Represents a loaded module's data."""
    def __init__(self, manifest, rules, sheets):
        self.id = manifest.get('id')
        self.name = manifest.get('name')
        self.version = manifest.get('version')
        self.description = manifest.get('description')
        self.entry = manifest.get('entry', {})
        self.dependencies = manifest.get('dependencies', [])

        self.rules = rules
        self.sheets = sheets

    def __repr__(self):
        return f"Module(id={self.id}, name={self.name}, version={self.version})"

class ModuleLoader:
    """Loads and manages modules for the VTT engine."""
    def __init__(self, action_manager, modules_directory="modules"):
        self.modules_directory = modules_directory
        self.action_manager = action_manager
        self.loaded_modules = {}

    def load_module(self, module_id):
        """Loads a single module by its ID (directory name)."""
        module_path = os.path.join(self.modules_directory, module_id)
        manifest_path = os.path.join(module_path, "module.json")

        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Module manifest not found at {manifest_path}")

        # Load manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Load rules
        rules = {}
        if 'rules' in manifest['entry']:
            rules_path = os.path.join(module_path, manifest['entry']['rules'])
            with open(rules_path, 'r') as f:
                rules = json.load(f)

        # Load sheets
        sheets = {}
        if 'sheets' in manifest['entry']:
            sheets_path = os.path.join(module_path, manifest['entry']['sheets'])
            with open(sheets_path, 'r') as f:
                sheets = json.load(f)

        # Load scripts and register actions
        if 'scripts' in manifest['entry'] and self.action_manager:
            for script_path_rel in manifest['entry']['scripts']:
                script_path_abs = os.path.join(module_path, script_path_rel)
                if os.path.exists(script_path_abs):
                    try:
                        result = subprocess.run(
                            ['node', script_path_abs],
                            capture_output=True,
                            text=True,
                            check=True,
                            encoding='utf-8'
                        )
                        actions_to_register = json.loads(result.stdout)
                        for action_data in actions_to_register:
                            self.action_manager.register_action(action_data)
                    except subprocess.CalledProcessError as e:
                        print(f"Error executing script {script_path_abs}: {e.stderr}")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON from {script_path_abs}: {e}")

        module = Module(manifest, rules, sheets)
        self.loaded_modules[module.id] = module
        print(f"Successfully loaded module: {module.name}")
        return module

    def get_module(self, module_id):
        """Retrieves a loaded module by its ID."""
        return self.loaded_modules.get(module_id)
