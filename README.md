# poe2-trade-agent

A web tool for saving Path of Exile 2 trade searches as templates. Pick mods from a list or paste a
trade URL, adjust the numbers, and open the search on the official trade site with one click. You
can sort templates into folders and tags, and share them in a public library where others can
browse, copy and upvote them.

## Local development

Requirements: Docker with Docker Compose, and [uv](https://docs.astral.sh/uv/).

### Database
- Starts a local PostgreSQL database.
```bash
docker compose up -d
```

- Shows the columns and indexes of the `user` table. Use `\dt` to list all tables.
```bash
docker compose exec db psql -U poe2_trade_agent -d poe2_trade_templates -c '\d "user"'
```

### Backend

```bash
cd backend
uv run fastapi dev app/main.py
```

- The API runs at: http://localhost:8000/api/v1
- Interactive API docs (Swagger) are at: http://localhost:8000/api/docs.

Running tests and linter

```bash
uv run pytest
uv run ruff format .
```

### Database migrations

```bash
uv run alembic revision --autogenerate -m "add user table"  # draft a new migration from the models
uv run alembic upgrade head                                 # update the database to the latest migration
```

### Mod list

Downloads the list of trade mods into the `mod` table. Run it once, and again after game patches.

```bash
uv run python -m app.commands.import_mods  # local
docker compose -f compose.prod.yml exec backend python -m app.commands.import_mods  # production server
```

- Mod data: [Exiled Exchange 2](https://github.com/Kvan7/Exiled-Exchange-2), MIT, © 2020 Alexander Drozdov.

## License

[MIT](LICENSE)

---

This product isn't affiliated with or endorsed by Grinding Gear Games in any way.
