"""
eToro Credential Setup — One-Time Migration to Windows Credential Manager
=========================================================================
Run this once to securely store your eToro API keys.
After this, etoro.json only holds non-sensitive config (account type).

Security model:
  - Keys are stored via Windows DPAPI (Data Protection API)
  - Encrypted at rest, tied to your Windows user account
  - Access is verified implicitly by your Windows login session
  - Other OS users on the same machine CANNOT read your credentials
  - No plain-text keys ever written to the filesystem after this runs
"""

import keyring
import json
import os
import sys
import getpass

SERVICE_NAME = "antigravity_etoro"

CREDENTIALS = {
    "ETORO_API_KEY":            "eToro Platform API Key (x-api-key header)",
    "ETORO_USER_API_KEY_REAL":  "eToro Real Account User Key (x-user-key header)",
    "ETORO_USER_API_KEY_DEMO":  "eToro Demo Account User Key (x-user-key header)",
}


def migrate_from_json():
    """Read existing keys from etoro.json (if present) and pre-fill prompts."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(script_dir, "..", "mcp", "etoro.json"))
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
        return data.get("env", {})
    except Exception:
        return {}


def _prompt_for_key(key: str, description: str, migrated: str) -> str:
    """Prompt the user for a credential value, using migrated value as default."""
    if migrated:
        print(f"  📋 {description}")
        print("     Found in etoro.json — press Enter to use it, or paste a new value.")
        new_val = getpass.getpass(f"     {key}: ")
        return new_val.strip() if new_val.strip() else migrated
    print(f"  🔑 {description}")
    return getpass.getpass(f"     {key}: ").strip()


def store_credentials(migrate: bool = True):
    print("\n🔐 eToro Credential Setup — Windows Credential Manager")
    print("=" * 58)
    print("Keys will be encrypted via Windows DPAPI.")
    print("Access is tied to your current Windows user account.\n")

    existing = migrate_from_json() if migrate else {}

    for key, description in CREDENTIALS.items():
        current = keyring.get_password(SERVICE_NAME, key)
        migrated = existing.get(key, "")

        if current:
            print(f"  ✅ {key} — already stored.")
            if input("     Overwrite? [y/N]: ").strip().lower() != "y":
                continue

        value = _prompt_for_key(key, description, migrated)

        if value:
            keyring.set_password(SERVICE_NAME, key, value)
            print("     ✅ Stored in Windows Credential Manager.\n")
        else:
            print("     ⚠️  Skipped (empty input).\n")

    print("\n✅ Setup complete. You can now safely remove keys from etoro.json.")
    print("   Run: python setup_credentials.py --verify to confirm storage.\n")


def verify_credentials():
    print("\n🔍 Verifying stored credentials...\n")
    all_ok = True
    for key in CREDENTIALS:
        val = keyring.get_password(SERVICE_NAME, key)
        if val:
            masked = val[:6] + "..." + val[-4:] if len(val) > 12 else "***"
            print(f"  ✅ {key}: {masked}")
        else:
            print(f"  ❌ {key}: NOT FOUND — run setup again.")
            all_ok = False
    print()
    return all_ok


def wipe_credentials():
    """Delete all stored eToro credentials from Windows Credential Manager."""
    print("\n🗑️  Wiping eToro credentials from Windows Credential Manager...")
    any_found = False
    for key in CREDENTIALS:
        try:
            keyring.delete_password(SERVICE_NAME, key)
            print(f"  ✅ {key} deleted.")
            any_found = True
        except keyring.errors.PasswordDeleteError:
            print(f"  —  {key} was not stored (skipped).")

    if any_found:
        print("\n⚠️  Credentials wiped. IMPORTANT: also rotate your eToro API keys online.")
        print("   eToro → Account Settings → API → Revoke & regenerate keys.")
    else:
        print("\n  Nothing to delete — no credentials were stored.")
    print()


def print_handover_checklist():
    print("""
📋 Pre-Handover Security Checklist
================================
[ ] 1. Run: python setup_credentials.py --wipe
         Removes keys from Windows Credential Manager.

[ ] 2. Rotate your eToro keys online:
         eToro → Account Settings → API → Revoke & Regenerate
         (Treat any key that touched this machine as compromised.)

[ ] 3. Delete or move this project folder off the machine:
         d:\\Projects\\Antigravity\\Financial AI\\

[ ] 4. Sign out of your Windows user account before handing over.
""")


def sanitize_json():
    """Remove real keys from etoro.json, leaving only account_type config."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(script_dir, "..", "mcp", "etoro.json"))
    template = {
        "_comment": "API keys are stored in Windows Credential Manager. Run setup_credentials.py to configure.",
        "env": {
            "ETORO_ACCOUNT_TYPE": "real"
        }
    }
    with open(config_path, "w") as f:
        json.dump(template, f, indent=2)
    print("  🧹 etoro.json sanitized — keys removed, only account type retained.")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify_credentials()
    elif "--wipe" in sys.argv:
        wipe_credentials()
    elif "--handover" in sys.argv:
        print_handover_checklist()
    elif "--sanitize" in sys.argv:
        sanitize_json()
    else:
        store_credentials(migrate=True)
        confirm = input("\nSanitize etoro.json now (remove plain-text keys)? [Y/n]: ").strip().lower()
        if confirm != "n":
            sanitize_json()
