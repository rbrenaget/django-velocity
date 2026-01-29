# Translations

## Prerequisites

The `makemessages` command requires GNU gettext tools. When using Docker, these are already included in the image. For local development without Docker, install gettext for your OS:

**Linux (Debian/Ubuntu)**:
```bash
sudo apt-get install gettext
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install gettext
```

**macOS**:
```bash
brew install gettext
brew link --force gettext
```

**Windows**:
Download and install from [GNU gettext for Windows](https://mlocati.github.io/articles/gettext-iconv-windows.html) or use WSL.

## Usage

Start by configuring the `LANGUAGES` setting in `base.py`, by uncommenting languages you are willing to support. Then, translation strings will be placed in this folder when running:

```bash
just makemessages
```

This should generate `django.po` (stands for Portable Object) files under each locale `<locale name>/LC_MESSAGES/django.po`. Each translatable string in the codebase is collected with its `msgid` and need to be translated as `msgstr`, for example:

```po
msgid "users"
msgstr "utilisateurs"
```

Once all translations are done, they need to be compiled into `.mo` files (stands for Machine Object), which are the actual binary files used by the application:

```bash
just compilemessages
```


Note that the `.po` files are NOT used by the application directly, so if the `.mo` files are out of date, the content won't appear as translated even if the `.po` files are up-to-date.

## Production

The production image runs `compilemessages` automatically at build time, so as long as your translated source files (PO) are up-to-date, you're good to go.


## Add a new language

1. Update the [`LANGUAGES` setting](https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-LANGUAGES) to your project's base settings.
2. Create the locale folder for the language next to this file, e.g. `fr_FR` for French. Make sure the case is correct.
3. Run `makemessages` (as instructed above) to generate the PO files for the new language.
