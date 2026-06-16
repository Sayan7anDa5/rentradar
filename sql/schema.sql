-- RentRadar normalized schema: cities -> localities -> listings
-- Idempotent: drops existing tables first so the file can be re-applied.

DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS localities;
DROP TABLE IF EXISTS cities;

CREATE TABLE cities (
    city_id  SERIAL PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE
);

CREATE TABLE localities (
    locality_id SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    city_id     INTEGER NOT NULL REFERENCES cities(city_id),
    UNIQUE (name, city_id)        -- a locality name can recur across cities
);

CREATE TABLE listings (
    listing_id  SERIAL PRIMARY KEY,
    locality_id INTEGER NOT NULL REFERENCES localities(locality_id),
    house_type  TEXT,
    area        NUMERIC(10,2),
    beds        INTEGER,
    bathrooms   INTEGER,
    balconies   INTEGER,
    furnishing  TEXT CHECK (furnishing IN ('Furnished','Semi-Furnished','Unfurnished')),
    area_rate   NUMERIC(12,2),
    rent        NUMERIC(12,2)
);

CREATE INDEX idx_localities_city   ON localities(city_id);
CREATE INDEX idx_listings_locality ON listings(locality_id);
