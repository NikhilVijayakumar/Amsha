import os
from pathlib import Path


def run_document_audit():
    root = Path(".")
    src_path = root / "src"
    # Adjusted to look for features which is the new standard
    docs_base = root / "docs" / "features"
    if not docs_base.exists():
        # Fallback to modules if features doesn't exist yet
        docs_base = root / "docs" / "modules"

    # Header Branding
    print("\n" + "=" * 70)
    print("📋  PROJECT DOCUMENTATION HEALTH AUDIT")
    print("=" * 70)
    print(f"{'MODULE NAME':<25} | {'STATUS':<12} | {'MISSING COMPONENTS'}")
    print("-" * 70)

    if not src_path.exists():
        print("❌ Error: 'src/' directory not found. Are you in the project root?")
        return

    # Filter for actual logic modules (exclude __pycache__, etc.)
    modules = []
    if src_path.exists():
         # Need to find the inner src root
         for possible_root in src_path.iterdir():
             if possible_root.is_dir() and not possible_root.name.startswith((".", "__")):
                 # Loop through packages in the root
                 for mod in possible_root.iterdir():
                      if mod.is_dir() and not mod.name.startswith((".", "__")):
                           modules.append(mod)

    if not modules:
        print("No modules found in src/.")
        return

    for mod in modules:
        mod_name = mod.name

        # Check for core artifacts
        has_readme = (docs_base / mod_name / "README.md").exists()
        has_test_specs = (root / "docs" / "test" / mod_name).exists()

        missing = []
        if not has_readme: missing.append("README.md")
        if not has_test_specs: missing.append("Test Scenarios")

        status = "✅ HEALTHY" if not missing else "❌ DEBT"
        missing_str = ", ".join(missing) if missing else "None"

        print(f"{mod_name:<25} | {status:<12} | {missing_str}")

    print("-" * 70)
    print("👉 Action: Use 'Document [Module]' to generate missing blueprints.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_document_audit()