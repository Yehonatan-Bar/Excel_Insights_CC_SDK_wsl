-- Migration: Add job_state column to analyses table
-- This stores the complete in-memory job state for persistence across sessions

ALTER TABLE analyses
ADD COLUMN IF NOT EXISTS job_state JSONB;

COMMENT ON COLUMN analyses.job_state IS 'Complete job state including events, messages, and progress for session persistence';

-- Add index for faster queries on active jobs
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
