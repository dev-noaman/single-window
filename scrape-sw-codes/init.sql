-- PostgreSQL init script for business activity codes

CREATE TABLE IF NOT EXISTS business_activity_codes (
  activity_code VARCHAR(255) PRIMARY KEY,
  industry_id VARCHAR(255),
  name_en TEXT,
  name_ar TEXT,
  description_en TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on activity_code for faster lookups
CREATE INDEX IF NOT EXISTS idx_activity_code ON business_activity_codes(activity_code);

-- Create index on updated_at for last update queries
CREATE INDEX IF NOT EXISTS idx_updated_at ON business_activity_codes(updated_at);
