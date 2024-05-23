#!/bin/bash

# Step 1: Create and activate a virtual environment
python3 -m venv env
source env/bin/activate

# Step 2: Install dependencies
pip install -r requirements.txt
pip install py2app

# Step 3: Clean previous builds
rm -rf build dist

# Step 4: Build the application
python setup.py py2app

# Step 5: Remove unnecessary library if causing issues
rm dist/Excelerate.app/Contents/Frameworks/liblzma.5.dylib

# Step 6: Sign individual frameworks
for framework in dist/Excelerate.app/Contents/Frameworks/*; do
    codesign --force --deep --sign - "$framework"
done

# Step 7: Sign the main executable
codesign --force --deep --sign - dist/Excelerate.app/Contents/MacOS/Excelerate

# Step 8: Sign the entire application
codesign --force --deep --sign - dist/Excelerate.app

# Step 9: Verify the signature
codesign --verify --verbose=4 dist/Excelerate.app

# Step 10: Create a ZIP archive for distribution
cd dist
zip -r Excelerate.zip Excelerate.app
cd ..

# Step 11: Generate SHA-256 hash for verification
shasum -a 256 dist/Excelerate.zip
