using System;
using System.Collections.Generic;

[Serializable]
public class Dialog
{
	public string text = null;
	public string img = null;
	public float imgHeight = -1;
	public int camX = -1;
	public int camY = -1;
	public string sound = null;
	public string video = null;
	public bool enableInteraction = false;

	public Dialog clone()
    {
		Dialog copy = new Dialog();
		copy.text = text;
		copy.img = img;
		copy.imgHeight = imgHeight;
		copy.camX = camX;
		copy.camY = camY;
		copy.sound = sound;
		copy.video = video;
		copy.enableInteraction = enableInteraction;
		return copy;
    }

	public bool isEqualTo(Dialog dialog)
    {
		return dialog.text == text && dialog.img == img && dialog.imgHeight == imgHeight && dialog.camX == camX && dialog.camY == camY && dialog.sound == sound && dialog.video == video && dialog.enableInteraction == enableInteraction;

	}
}

[Serializable]
public class DataLevel
{
	public string src;
	public string name;
	public List<Dialog> overridedDialogs = null;

	public DataLevel clone()
	{
		DataLevel copy = new DataLevel();
		copy.src = src;
		copy.name = name;
		if (overridedDialogs != null)
		{
			copy.overridedDialogs = new List<Dialog>();
			foreach (Dialog dialog in overridedDialogs)
				copy.overridedDialogs.Add(dialog.clone());
		}
		return copy;
	}

	public bool dialogsEqualsTo (List<Dialog> checkDialogs)
    {
		if (checkDialogs.Count != overridedDialogs.Count)
			return false;
        else
        {
			for (int i = 0; i < overridedDialogs.Count; i++)
				if (!overridedDialogs[i].isEqualTo(checkDialogs[i]))
					return false;
			return true;
        }
    }
}