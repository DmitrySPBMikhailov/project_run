runlocal:
	python manage.py runserver --settings=project_run.settings.local

makemigrations:
	python manage.py makemigrations --settings=project_run.settings.local

migrate:
	python manage.py migrate --settings=project_run.settings.local

createsuperuser:
	python manage.py createsuperuser --settings=project_run.settings.local

test:
	python manage.py test --settings=project_run.settings.local