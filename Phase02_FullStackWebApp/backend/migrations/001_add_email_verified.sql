-- Migration: Add email_verified field to users table
-- Date: 2026-01-07
-- Description: Add email verification support for Better Auth integration

-- Add email_verified column (defaults to FALSE for new users)
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Mark all existing users as verified (Option B: Instant Switch)
-- This ensures existing users can continue using the app without interruption
UPDATE users
SET email_verified = TRUE
WHERE email_verified = FALSE;

-- Create index for faster lookups on email_verified status
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified);

-- Verify migration
SELECT COUNT(*) as total_users,
       SUM(CASE WHEN email_verified THEN 1 ELSE 0 END) as verified_users
FROM users;
