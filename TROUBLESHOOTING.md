# WeatherBot Troubleshooting Guide

## Common Issues and Solutions

### 1. **Frontend: `npm start` Error - "Could not read package.json"**

**Error:**
```
npm error code ENOENT
npm error syscall open
npm error path /home/.../WeatherBot/package.json
npm error errno -2
```

**Solution:**
You're trying to run `npm start` from the wrong directory. The frontend has its own package.json.

```bash
# ❌ Wrong - from root directory
npm start

# ✅ Correct - from frontend directory
cd frontend
npm start
```

### 2. **Frontend: Dependency Resolution Issues**

**Error:**
```
npm error ERESOLVE could not resolve
npm error While resolving: framer-motion@...
```

**Solution:**
Use the legacy peer deps flag:

```bash
cd frontend
npm install --legacy-peer-deps
```

### 3. **Backend: Missing Environment Variables**

**Error:**
```
OpenAI API Key set: No
OpenWeather API Key set: No
```

**Solution:**
Create a `backend/config.env` file with your API keys:

```bash
cd backend
touch config.env
```

Add your keys to `config.env`:
```
OPENAI_API_KEY=your_openai_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
```

### 4. **Backend: Virtual Environment Issues**

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
Make sure you're in the virtual environment:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. **Port Already in Use**

**Error:**
```
Address already in use: ('127.0.0.1', 8000)
```

**Solution:**
Find and stop the process using the port:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 PID

# Or kill all Python processes (be careful!)
pkill -f python
```

### 6. **CORS Issues**

**Error:**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
This is already handled in the backend, but if you see this:

1. Make sure backend is running on port 8000
2. Check that CORS middleware is properly configured
3. Restart both frontend and backend

### 7. **API Connection Issues**

**Symptoms:**
- Red connection indicator
- "Couldn't connect to the server" messages

**Solutions:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API keys are configured:**
   - Verify `backend/config.env` exists
   - Check keys are valid

3. **Restart services:**
   ```bash
   # Use the convenience script
   ./start-dev.sh
   
   # Or manually
   cd backend && python run.py &
   cd frontend && npm start
   ```

### 8. **React Compilation Errors**

**Error:**
```
Module not found: Can't resolve './QuickSuggestions'
```

**Solution:**
Make sure all files are created:

```bash
# Check if QuickSuggestions.js exists
ls frontend/src/QuickSuggestions.js

# If missing, the file should be created with the component code
```

### 9. **Weather Icons Not Showing**

**Symptoms:**
- Missing weather icons in chat responses

**Solution:**
Ensure react-icons is properly installed:

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

### 10. **Dark Mode Not Persisting**

**Symptoms:**
- Theme resets on page refresh

**Solution:**
This might be a browser storage issue:

1. Check browser console for localStorage errors
2. Clear browser cache and try again
3. Make sure you're not in incognito mode

## Quick Fixes

### Reset Everything
```bash
# Stop all processes
pkill -f "node\|python"

# Clean frontend
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Clean backend
cd ../backend
deactivate  # if in venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start fresh
cd ..
./start-dev.sh
```

### Check Service Status
```bash
# Backend health
curl http://localhost:8000/health

# Frontend status
curl http://localhost:3000

# Check processes
ps aux | grep -E "(node|python)"
```

### Logs and Debugging

1. **Backend logs:** Check terminal where `python run.py` is running
2. **Frontend logs:** Check browser console (F12)
3. **Network requests:** Check browser Network tab
4. **API responses:** Use browser DevTools or curl

## Getting Help

If you're still having issues:

1. **Check the terminal output** for specific error messages
2. **Check browser console** for JavaScript errors
3. **Verify API keys** are correctly set
4. **Ensure all dependencies** are installed
5. **Try the convenience script:** `./start-dev.sh`

## Development Tips

### Useful Commands
```bash
# Start both services easily
./start-dev.sh

# Backend only
cd backend && source venv/bin/activate && python run.py

# Frontend only
cd frontend && npm start

# Check what's running on ports
lsof -i :3000,8000

# Full restart
pkill -f "node\|python" && ./start-dev.sh
```

### IDE Setup
- Use VSCode with ES7+ React/Redux/React-Native snippets
- Install Python extension for backend development
- Consider using Thunder Client or Postman for API testing

### Performance Tips
- Keep browser DevTools closed when not debugging
- Use `npm run build` for production builds
- Monitor browser memory usage for large chat histories 