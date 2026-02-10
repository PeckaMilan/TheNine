# LEGO Module Operations

Manage reusable GCP/AI modules across projects.

## Quick Reference

**Central Repo:** `C:\Users\mpeck\PycharmProjects\mpeck-lego`

## Commands

### Sync All Projects

```bash
python /c/Users/mpeck/PycharmProjects/mpeck-lego/sync.py
```

### List Projects

```bash
python /c/Users/mpeck/PycharmProjects/mpeck-lego/sync.py --list
```

### Sync Specific Project

```bash
python /c/Users/mpeck/PycharmProjects/mpeck-lego/sync.py --project council-watch
```

### Dry Run (Preview)

```bash
python /c/Users/mpeck/PycharmProjects/mpeck-lego/sync.py --dry-run
```

---

## Available Modules

| Module | Description | Import |
|--------|-------------|--------|
| `gemini.py` | Gemini AI generation | `from lego.gemini import generate, generate_json` |
| `firestore.py` | Firestore CRUD | `from lego.firestore import get_doc, set_doc` |
| `storage.py` | Cloud Storage | `from lego.storage import upload_blob` |
| `auth.py` | Firebase Auth | `from lego.auth import verify_token` |
| `billing.py` | Stripe payments | `from lego.billing import create_checkout` |
| `scraper.py` | URL to Markdown | `from lego.scraper import url_to_markdown` |
| `secrets.py` | Secret Manager | `from lego.secrets import get_secret` |
| `deploy.py` | Cloud Run deploy | `from lego.deploy import deploy_cloud_run` |

## Module Groups

Configure in `mpeck-lego/registry.json`:

```json
{
  "projects": {
    "../YourProject": ["core", "gcp"]
  },
  "groups": {
    "core": ["__init__.py", "base_config.py", "secrets.py", "logging.py", "deploy.py"],
    "gcp": ["auth.py", "firestore.py", "storage.py", "gemini.py"],
    "billing": ["billing.py"],
    "scraper": ["scraper.py"]
  }
}
```

---

## Adding New Project to LEGO

1. Open `C:\Users\mpeck\PycharmProjects\mpeck-lego\registry.json`
2. Add entry:
   ```json
   "../NewProject": ["core", "gcp"]
   ```
3. Run sync:
   ```bash
   python /c/Users/mpeck/PycharmProjects/mpeck-lego/sync.py
   ```

---

## Creating New Module

1. Create `mpeck-lego/lego/new_module.py` (single file, <300 lines)
2. Add to group in `registry.json`
3. Update `lego/__init__.py` with lazy import:
   ```python
   try:
       from . import new_module
   except ImportError:
       new_module = None
   ```
4. Run `sync.py`

---

## Rules

- **NEVER** edit `lego/` files in target projects
- **ALWAYS** edit in `mpeck-lego/lego/` and sync
- Keep modules **single-file** and **async-first**
- Use **dependency injection** (pass config, no globals)
