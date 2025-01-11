using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;

public class DashboardLauncher : MonoBehaviour
{
    // Relative path to the Flask script
    private string flaskScriptRelativePath = "/Script/Dashboard/visualization/app.py";

    // Local URL where the Flask app is hosted
    private string flaskUrl = "http://127.0.0.1:5050";

    // Method triggered when the button is clicked
    public void OnButtonClick()
    {
        // Start the Flask application
        StartFlaskApp();

        // Open the Flask app in the default web browser
        OpenBrowser();
    }

    // Method to start the Flask application
    private void StartFlaskApp()
    {
        // Construct the absolute path to the Flask script
        string flaskScriptPath = Application.dataPath + flaskScriptRelativePath;

        // Use the terminal to run the Python script
        ProcessStartInfo startInfo = new ProcessStartInfo
        {
            FileName = "python",                      // Assuming 'python' is in PATH
            Arguments = $"\"{flaskScriptPath}\"",     // Use the script path as argument
            UseShellExecute = false,                 // Do not use the shell to execute
            RedirectStandardOutput = true,           // Redirect standard output (optional)
            RedirectStandardError = true,            // Redirect standard error (optional)
            CreateNoWindow = false                   // Show the terminal window for debugging
        };

        // Start the process
        Process process = new Process { StartInfo = startInfo };
        process.Start();
    }

    // Method to open the Flask app in the default web browser
    private void OpenBrowser()
    {
        // Open the specified URL in the system's default web browser
        Application.OpenURL(flaskUrl);
    }
}