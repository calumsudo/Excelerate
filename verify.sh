#!/bin/bash

# Temporarily disable Gatekeeper for testing
sudo spctl --master-disable

# Move the app to the /Applications directory if not already done
mv ~/Downloads/Excelerate.app /Applications/

# Re-sign the application
codesign --force --deep --sign - /Applications/Excelerate.app

# Verify the signature
codesign --verify --verbose=4 /Applications/Excelerate.app

# Run the application from Terminal to check for errors
cd /Applications/Excelerate.app/Contents/MacOS/
./Excelerate

# Re-enable Gatekeeper after testing
sudo spctl --master-enable
