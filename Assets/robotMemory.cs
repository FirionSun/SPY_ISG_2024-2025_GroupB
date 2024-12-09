using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class robotMemory : MonoBehaviour
{
    // Advice: FYFY component aims to contain only public members (according to Entity-Component-System paradigm).
    public Dictionary<string, List<string>> memory= new Dictionary<string, List<string>>();
}
