# Important: Set Python Version in Render

The `runtime.txt` file might not be detected. You need to set the Python version in Render's dashboard:

## Steps:

1. **Go to your Render service dashboard**
2. **Click "Environment"** tab (or "Settings" → "Environment")
3. **Add Environment Variable**:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.9`
4. **Save Changes**
5. **Redeploy** (or it will auto-redeploy)

This will force Render to use Python 3.11.9 instead of 3.13.4.

---

**Alternative**: You can also set it in the service settings under "Build & Deploy" → "Python Version" if that option is available.

