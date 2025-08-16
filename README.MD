# Use shortcut commands

You can run the project locally using **Makefile**.

## Start project on a local server

```bash
make runlocal
```

Under the hood, this command executes:

```bash
python manage.py runserver --settings=project_run.settings.local
```

## Migrate DB

```bash
make migrate
```

Under the hood, this command executes:

```bash
python manage.py migrate --settings=project_run.settings.local
```

## Create Superuser

```bash
make createsuperuser
```

Under the hood, this command executes:

```bash
python manage.py createsuperuser --settings=project_run.settings.local
```
