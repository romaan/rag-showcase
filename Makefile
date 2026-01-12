.PHONY: up down dev migrate ingest_local ingest_urls

up:
	docker compose up -d

down:
	docker compose down -v

migrate:
	python -m scripts.ingest_local --migrate-only

dev:
	uvicorn app.main:app --reload --port 8000

ingest_local:
	python -m scripts.ingest_local --path ./data/docs

ingest_urls:
	python -m scripts.ingest_urls --urls-file ./data/urls.txt
