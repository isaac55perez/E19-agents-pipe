#!/bin/bash
echo "=========================================="
echo "Agent1 Implementation Verification"
echo "=========================================="
echo ""

echo "1. Checking file structure..."
files=(
    "__init__.py"
    "extractor.py"
    "test_extractor.py"
    "main.py"
    "README.md"
    "PLAN.md"
    "IMPLEMENTATION_SUMMARY.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
    fi
done

echo ""
echo "2. Running tests..."
python -m pytest test_extractor.py -q

echo ""
echo "3. Testing standalone execution..."
python main.py > /tmp/agent_output.log 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Standalone execution successful"
else
    echo "   ❌ Standalone execution failed"
fi

echo ""
echo "4. Checking Excel output..."
if [ -f "output/output12.xlsx" ]; then
    size=$(stat -c%s "output/output12.xlsx")
    echo "   ✅ Excel file created ($size bytes)"
else
    echo "   ❌ Excel file not found"
fi

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
