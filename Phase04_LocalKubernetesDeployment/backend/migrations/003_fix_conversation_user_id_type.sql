-- Migration: Fix conversation and message table user_id column types to match UUID in users table
-- This migration changes the user_id columns from VARCHAR to UUID to match the users.id type

-- Drop foreign key constraints first
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS fk_conversations_user_id;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS fk_messages_user_id;

-- Update user_id column types from VARCHAR to UUID in both tables
-- First, ensure all existing user_id values can be cast to UUID format
-- Then change the column types
ALTER TABLE conversations ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
ALTER TABLE messages ALTER COLUMN user_id TYPE UUID USING user_id::UUID;

-- Recreate foreign key constraints with proper types
ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE messages ADD CONSTRAINT fk_messages_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Confirmation query
SELECT 'Conversation and message user_id columns updated to UUID type successfully' as result;