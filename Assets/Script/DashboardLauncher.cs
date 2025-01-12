using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;

public class DashboardLauncher : MonoBehaviour
{
    // Command to run the Flask app
    private string flaskCommand = "python"; // 替换为你的 Python 路径
    private string flaskScriptRelativePath = "/Script/Dashboard/visualization/app.py";

    // Local URL where the Flask app is hosted
    private string flaskUrl = "http://192.168.251.195:5056";

    // Method triggered when the button is clicked
    public void OnButtonClick()
    {
        // Run Flask command in the terminal
        RunCommand();

        // Open the Flask app in the default web browser
        OpenBrowser();
    }

    // Method to run the command in the terminal
    private void RunCommand()
{
     string flaskScriptPath = "/Users/romai/Documents/MIPI/M2/ISG/SPY_ISG_2024-2025_GroupB/Assets/Script/Dashboard/visualization/app.py";

    UnityEngine.Debug.Log($"Running command: {flaskCommand} {flaskScriptPath}");

    ProcessStartInfo startInfo = new ProcessStartInfo
    {
        FileName = "/bin/bash", // 使用 bash 执行命令
        Arguments = $"-c \"{flaskCommand} {flaskScriptPath}\"",
        UseShellExecute = false,
        RedirectStandardOutput = true, // 捕获标准输出
        RedirectStandardError = true,  // 捕获标准错误
        CreateNoWindow = true
    };

    try
    {
        Process process = new Process { StartInfo = startInfo };
        process.OutputDataReceived += (sender, args) =>
        {
            if (!string.IsNullOrEmpty(args.Data))
            {
                UnityEngine.Debug.Log($"[Python stdout] {args.Data}");
            }
        };
        process.ErrorDataReceived += (sender, args) =>
        {
            if (!string.IsNullOrEmpty(args.Data))
            {
                UnityEngine.Debug.LogError($"[Python stderr] {args.Data}");
            }
        };

        process.Start();
        process.BeginOutputReadLine(); // 开始异步读取 stdout
        process.BeginErrorReadLine();  // 开始异步读取 stderr

        UnityEngine.Debug.Log("Flask app started, waiting for logs...");
    }
    catch (System.Exception e)
    {
        UnityEngine.Debug.LogError($"Failed to run command: {e.Message}\n{e.StackTrace}");
    }
}


    // Method to open the Flask app in the default web browser
    private void OpenBrowser()
    {
        UnityEngine.Debug.Log($"Opening browser at: {flaskUrl}");
        Application.OpenURL(flaskUrl);
    }
}