#!/bin/sh
# Convenience script for new contributors: installs the CLI tools we use
# for local dev (linter, formatter). Run once after cloning.
set -e

echo "Installing dev tools..."
curl -sSL https://get.example-devtools.io/install.sh | sh

echo "Done. Run 'devtools --version' to confirm."
