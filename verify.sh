#!/bin/bash
# Verification script for UMatch Financial Control System

echo "🔍 Verifying UMatch Financial Control System..."
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "   ✅ Python 3 is installed"
else
    echo "   ❌ Python 3 is not installed"
    exit 1
fi

# Check Node version
echo ""
echo "2️⃣  Checking Node.js version..."
node --version
if [ $? -eq 0 ]; then
    echo "   ✅ Node.js is installed"
else
    echo "   ❌ Node.js is not installed"
    exit 1
fi

# Check backend
echo ""
echo "3️⃣  Checking backend..."
cd backend
python3 -c "import main" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Backend imports successfully"
else
    echo "   ❌ Backend has import errors"
    exit 1
fi

# Check backend dependencies
echo ""
echo "4️⃣  Checking backend dependencies..."
pip3 list | grep -E "(fastapi|uvicorn|pandas)" > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Backend dependencies installed"
else
    echo "   ⚠️  Some backend dependencies missing - run: cd backend && pip3 install -r requirements.txt"
fi

# Check frontend
cd ../frontend
echo ""
echo "5️⃣  Checking frontend..."
if [ -d "node_modules" ]; then
    echo "   ✅ Frontend dependencies installed"
else
    echo "   ⚠️  Frontend dependencies missing - run: cd frontend && npm install"
fi

if [ -d "dist" ]; then
    echo "   ✅ Frontend build exists"
else
    echo "   ⚠️  Frontend not built - run: cd frontend && npm run build"
fi

# Check configuration
cd ..
echo ""
echo "6️⃣  Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ⚠️  No .env file - copy .env.example to .env and configure"
fi

echo ""
echo "✅ Verification complete!"
echo ""
echo "📚 To start the application:"
echo "   Backend:  cd backend && python3 main.py"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "📖 See README.md for more information"
