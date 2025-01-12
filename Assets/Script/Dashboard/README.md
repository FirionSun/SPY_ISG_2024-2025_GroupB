# **Launching the Dashboard**

This document explains how to launch and troubleshoot the dashboard from the SPY main page or directly via the terminal.

## **Required Packages**

Before running the dashboard, ensure you have the necessary Python packages installed.

To install these packages, run the following command:

```bash
pip install flask plotly pandas requests
```
---

## **From the SPY Main Page**

- Click the **"Dashboard"** button to automatically execute the following command:
  ```bash
  python Assets/Script/Dashboard/visualization/app.py --host 0.0.0.0 --port 8080
- This will start the dashboard and open it in your default browser.
- In case of issue (e.g., routing problems or incorrect Python paths), try to use the command in terminal directly. Change host and port if needed.