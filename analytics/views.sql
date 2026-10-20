-- Views over the Phase 1 outputs. For interactive use from the repo root:
--   duckdb -init analytics/views.sql
-- `dip cuad-report` creates the same views (from the configured data dir) before
-- running the queries in analytics/queries/.
CREATE OR REPLACE VIEW gold_fields  AS SELECT * FROM 'data/gold/gold_fields.parquet';
CREATE OR REPLACE VIEW documents    AS SELECT * FROM 'data/gold/documents.parquet';
CREATE OR REPLACE VIEW label_issues AS SELECT * FROM 'data/gold/label_issues.parquet';
CREATE OR REPLACE VIEW text_layer   AS SELECT * FROM 'data/profiles/text_layer.parquet';
CREATE OR REPLACE VIEW splits AS
    SELECT unnest(ids) AS doc_id, split
    FROM (
        SELECT unnest(map_keys(s)) AS split, unnest(map_values(s)) AS ids
        FROM (SELECT splits::MAP(VARCHAR, VARCHAR[]) AS s FROM read_json('data/splits.json'))
    );
