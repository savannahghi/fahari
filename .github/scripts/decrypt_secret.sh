#!/bin/sh

# Decrypt the file
mkdir $GITHUB_WORKSPACE/secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --verbose --batch --yes --decrypt --passphrase="$SECRET_PASSPHRASE" --output $GITHUB_WORKSPACE/secrets/gcs.json gcs.json.gpg
