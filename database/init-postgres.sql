CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_parties_name ON parties (name);
CREATE INDEX IF NOT EXISTS idx_parties_created_at ON parties (created_at);

CREATE TABLE IF NOT EXISTS calculations (
    id SERIAL PRIMARY KEY,
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    total_votes INTEGER NOT NULL CHECK (total_votes >= 0),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calculations_timestamp ON calculations (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_calculations_total_seats ON calculations (total_seats);

CREATE TABLE IF NOT EXISTS voting_submissions (
    id SERIAL PRIMARY KEY,
    party_id INTEGER NOT NULL,
    votes INTEGER NOT NULL CHECK (votes >= 0),
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_voting_submissions_party
        FOREIGN KEY (party_id)
        REFERENCES parties(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_voting_submissions_party_id ON voting_submissions (party_id);
CREATE INDEX IF NOT EXISTS idx_voting_submissions_submitted_at ON voting_submissions (submitted_at DESC);

CREATE TABLE IF NOT EXISTS calculation_results (
    id SERIAL PRIMARY KEY,
    calculation_id INTEGER NOT NULL,
    party_id INTEGER NOT NULL,
    votes INTEGER NOT NULL CHECK (votes >= 0),
    seats INTEGER NOT NULL CHECK (seats >= 0),

    CONSTRAINT fk_calculation_results_calculation
        FOREIGN KEY (calculation_id)
        REFERENCES calculations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_calculation_results_party
        FOREIGN KEY (party_id)
        REFERENCES parties(id)
        ON DELETE CASCADE,

    -- Unique constraint: one result per party per calculation
    CONSTRAINT uq_calculation_party UNIQUE (calculation_id, party_id)
);

CREATE INDEX IF NOT EXISTS idx_calculation_results_calculation_id ON calculation_results (calculation_id);
CREATE INDEX IF NOT EXISTS idx_calculation_results_party_id ON calculation_results (party_id);
CREATE INDEX IF NOT EXISTS idx_calculation_results_calc_party ON calculation_results (calculation_id, party_id);
CREATE INDEX IF NOT EXISTS idx_calculation_results_seats ON calculation_results (seats);


-- HELPER FUNCTIONS
-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update parties.updated_at
CREATE TRIGGER update_parties_updated_at
    BEFORE UPDATE ON parties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- SEED PREDEFINED PARTIES
INSERT INTO parties (name) VALUES
    ('Lista A'),
    ('Lista B'),
    ('Lista C'),
    ('Lista D'),
    ('Lista E'),
    ('Lista F'),
    ('Lista G'),
    ('Lista H'),
    ('Lista I'),
    ('Lista J')
ON CONFLICT (name) DO NOTHING;
