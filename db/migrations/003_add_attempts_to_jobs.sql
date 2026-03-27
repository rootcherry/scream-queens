-- 003_add_attempts_to_jobs.sql
-- Migration: add attempts column to jobs table for retry support
-- Safe: only adds column if it does not exist

ALTER TABLE jobs
ADD COLUMN attempts INTEGER DEFAULT 0;
