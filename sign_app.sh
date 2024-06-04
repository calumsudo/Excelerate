# #!/bin/bash

# # Define the output log file
# LOG_FILE="build_output.txt"

# # Redirect all output to the log file
# exec > >(tee -i $LOG_FILE) 2>&1

# # Step 1: Create and activate a virtual environment
# echo "Creating virtual environment..."
# python3 -m venv env
# source env/bin/activate

# # Step 2: Upgrade pip and install wheel
# echo "Upgrading pip and installing wheel..."
# pip install --upgrade pip
# pip install wheel

# # Step 3: Install dependencies
# echo "Installing dependencies..."
# pip install customtkinter==5.2.2
# pip install msal==1.28.0
# pip install openpyxl==3.1.2
# pip install pandas==2.2.2
# pip install pillow==10.3.0
# pip install PyPDF2==3.0.1
# pip install pyperclip==1.8.2
# pip install reportlab==4.2.0
# pip install tkcalendar==1.6.1
# pip install wheel==0.43.0

# # Step 4: Clean previous builds
# echo "Cleaning previous builds..."
# rm -rf build dist

# # Step 5: Build the application
# echo "Building the application..."
# python setup.py py2app

# # Step 6: Ensure Tcl/Tk libraries are included
# echo "Ensuring Tcl/Tk libraries are included..."
# if [ -d "$(dirname $(which python))/../lib/tcl8.6" ]; then
#     cp -R "$(dirname $(which python))/../lib/tcl8.6" dist/Excelerate.app/Contents/Resources/lib/
# fi
# if [ -d "$(dirname $(which python))/../lib/tk8.6" ]; then
#     cp -R "$(dirname $(which python))/../lib/tk8.6" dist/Excelerate.app/Contents/Resources/lib/
# fi

# # Step 7: Remove unnecessary library if causing issues
# echo "Removing unnecessary libraries..."
# rm dist/Excelerate.app/Contents/Frameworks/liblzma.5.dylib

# # Step 8: Sign individual frameworks
# echo "Signing individual frameworks..."
# for framework in dist/Excelerate.app/Contents/Frameworks/*; do
#     codesign --force --deep --sign - "$framework"
# done

# # Step 9: Sign the main executable
# echo "Signing the main executable..."
# codesign --force --deep --sign - dist/Excelerate.app/Contents/MacOS/Excelerate

# # Step 10: Sign the entire application
# echo "Signing the entire application..."
# codesign --force --deep --sign - dist/Excelerate.app

# # Step 11: Verify the signature
# echo "Verifying the signature..."
# codesign --verify --verbose=4 dist/Excelerate.app

# # Step 12: Create a ZIP archive for distribution
# echo "Creating ZIP archive for distribution..."
# cd dist
# zip -r Excelerate.zip Excelerate.app
# cd ..

# # Step 13: Generate SHA-256 hash for verification
# echo "Generating SHA-256 hash for verification..."
# shasum -a 256 dist/Excelerate.zip

# echo "Build process completed. Check the log file $LOG_FILE for details."


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