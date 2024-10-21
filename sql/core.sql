CREATE USER json_editor WITH login PASSWORD 'Lokdhathri#123';

DROP database stories;

CREATE DATABASE json_editor;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO json_editor;

GRANT ALL PRIVILEGES ON DATABASE json_editor TO json_editor;

GRANT ALL ON DATABASE json_editor TO json_editor;

ALTER ROLE json_editor CREATEDB;