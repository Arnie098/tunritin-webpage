#!/usr/bin/env bash

# Generate config.js from environment variables
echo "const SUPABASE_CONFIG = {
    URL: '$SUPABASE_URL',
    KEY: '$SUPABASE_KEY'
};" > config.js

echo "config.js generated successfully."
