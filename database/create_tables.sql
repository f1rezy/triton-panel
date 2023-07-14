CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY,
    name VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
    id UUID PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    model_id UUID NOT NULL REFERENCES models(id),
    upload_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS triton_loaded (
    id UUID PRIMARY KEY,
    version_id UUID NOT NULL REFERENCES versions(id)
);