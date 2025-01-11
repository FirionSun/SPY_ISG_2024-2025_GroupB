using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;

public class DashboardLauncher : MonoBehaviour
{
    // Relative path to the Flask script
    private string flaskScriptRelativePath = "/Script/Dashboard/visualization/app.py &";

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
        string flaskScriptPath = Application.dataPath + flaskScriptRelativePath;

        UnityEngine.Debug.Log($"Attempting to start Flask script at: {flaskScriptPath}");

        ProcessStartInfo startInfo = new ProcessStartInfo
        {
            FileName = "python3",
            Arguments = $"\"{flaskScriptPath}\"",
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        try
        {
            Process process = new Process { StartInfo = startInfo };
            process.Start();

            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();

            UnityEngine.Debug.Log($"Flask Output: {output}");
            UnityEngine.Debug.Log($"Flask Error: {error}");
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError($"Failed to start Flask application: {e.Message}");
        }
    }

    // Method to open the Flask app in the default web browser
    private void OpenBrowser()
    {
        // Open the specified URL in the system's default web browser
        Application.OpenURL(flaskUrl);
    }
}