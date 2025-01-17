﻿using UnityEngine;
using System.Collections.Generic;
using TMPro;
using FYFY;

/// <summary>
/// This system executes new currentActions
/// </summary>
public class CurrentActionExecutor : FSystem {
	private Family f_wall = FamilyManager.getFamily(new AllOfComponents(typeof(Position)), new AnyOfTags("Wall", "Door"), new AnyOfProperties(PropertyMatcher.PROPERTY.ACTIVE_IN_HIERARCHY));
	private Family f_activableConsole = FamilyManager.getFamily(new AllOfComponents(typeof(Activable),typeof(Position),typeof(AudioSource)));
    private Family f_newCurrentAction = FamilyManager.getFamily(new AllOfComponents(typeof(CurrentAction), typeof(BasicAction)));
	private Family f_agent = FamilyManager.getFamily(new AllOfComponents(typeof(ScriptRef), typeof(Position)));

	protected override void onStart()
	{
		f_newCurrentAction.addEntryCallback(onNewCurrentAction);
		Pause = true;
	}

	protected override void onProcess(int familiesUpdateCount)
	{
		foreach (GameObject agent in f_agent)
		{
			// count inaction if a robot have no CurrentAction
			if (agent.tag == "Player" && agent.GetComponent<ScriptRef>().executableScript.GetComponentInChildren<CurrentAction>(true) == null)
				agent.GetComponent<ScriptRef>().nbOfInactions++;
			// Cancel move if target position is used by another agent
			bool conflict = true;
			while (conflict)
			{
				conflict = false;
				foreach (GameObject agent2 in f_agent)
					if (agent != agent2 && agent.tag == agent2.tag && agent.tag == "Player")
					{
						Position r1Pos = agent.GetComponent<Position>();
						Position r2Pos = agent2.GetComponent<Position>();
						// check if the two robots move on the same position => forbiden
						if (r2Pos.targetX != -1 && r2Pos.targetY != -1 && r1Pos.targetX == r2Pos.targetX && r1Pos.targetY == r2Pos.targetY)
						{
							r2Pos.targetX = -1;
							r2Pos.targetY = -1;
							conflict = true;
							GameObjectManager.addComponent<ForceMoveAnimation>(agent2);
						}
						// one robot doesn't move and the other try to move on its position => forbiden
						else if (r2Pos.targetX == -1 && r2Pos.targetY == -1 && r1Pos.targetX == r2Pos.x && r1Pos.targetY == r2Pos.y)
						{
							r1Pos.targetX = -1;
							r1Pos.targetY = -1;
							conflict = true;
							GameObjectManager.addComponent<ForceMoveAnimation>(agent);
						}
						// the two robot want to exchange their position => forbiden
						else if (r1Pos.targetX == r2Pos.x && r1Pos.targetY == r2Pos.y && r1Pos.x == r2Pos.targetX && r1Pos.y == r2Pos.targetY)
                        {
							r1Pos.targetX = -1;
							r1Pos.targetY = -1;
							r2Pos.targetX = -1;
							r2Pos.targetY = -1;
							conflict = true;
							GameObjectManager.addComponent<ForceMoveAnimation>(agent);
							GameObjectManager.addComponent<ForceMoveAnimation>(agent2);
						}

					}
			}
		}

		// Record valid movements
		foreach (GameObject robot in f_agent)
		{
			Position pos = robot.GetComponent<Position>();
			if (pos.targetX != -1 && pos.targetY != -1)
			{
				pos.x = pos.targetX;
				pos.y = pos.targetY;
				pos.targetX = -1;
				pos.targetY = -1;
			}
		}
		Pause = true;
	}

	// each time a new currentAction is added, 
	private void onNewCurrentAction(GameObject currentAction) {
		Pause = false; // activates onProcess to identify inactive robots
		
		CurrentAction ca = currentAction.GetComponent<CurrentAction>();
        // process action depending on action type
		switch (currentAction.GetComponent<BasicAction>().actionType){
			case BasicAction.ActionType.Forward:
				ApplyForward(ca.agent);
				break;
			case BasicAction.ActionType.TurnLeft:
				ApplyTurnLeft(ca.agent);
				break;
			case BasicAction.ActionType.TurnRight:
				ApplyTurnRight(ca.agent);
				break;
			case BasicAction.ActionType.TurnBack:
				ApplyTurnBack(ca.agent);
				break;
			case BasicAction.ActionType.Wait:
				break;
			case BasicAction.ActionType.VarInt:
				//Add int variable processsing
				if (ca.agent.GetComponent<robotMemory>())
				{
					// check si variable déifni
					string s;
					if (ca.GetComponentInChildren<TMP_InputField>().text == "")
					{
						s = "0";
						Debug.Log("int no init " + s);
					}
					else
					{
						s = ca.transform.GetComponentInChildren<TMP_InputField>().text;
						Debug.Log("Value found : " + s);
					}
					// check si int existe déjà dans la mémoire
					if (!ca.agent.GetComponent<robotMemory>().memory.ContainsKey("int"))
					{
						Debug.Log("Not found in memo");
						List<string> ls = new List<string>();	
						ls.Add(s);
						Debug.Log("Added variable int of value " + s);
						ca.agent.GetComponent<robotMemory>().memory.Add("int", ls);
					}
					else{
						Debug.Log("Found in memo");
						// List<string> ls = ca.agent.GetComponent<robotMemory>().memory["int"];
						// ls.Add(s);
						ca.agent.GetComponent<robotMemory>().memory["int"].Add(s);
						Debug.Log("Added variable int of value " + s);
					
					}

					// tooltip
					TooltipContent tooltipContent = ca.agent.GetComponentInChildren<TooltipContent>();
					robotMemory robotMem = ca.agent.GetComponent<robotMemory>();
					
					string valueInt = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("int")){
						valueInt = valueInt + "int : ";
						for (int i = 0; i < robotMem.memory["int"].Count; i++){
							valueInt = valueInt + robotMem.memory["int"][i];
							if (i < robotMem.memory["int"].Count - 1)
								valueInt = valueInt + ", ";
						}
						valueInt = valueInt + "\n";
					}

					string valueBool = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("boolean")){
						valueBool = valueBool + "boolean : ";
						for (int i = 0; i < robotMem.memory["boolean"].Count; i++){
							valueBool = valueBool + robotMem.memory["boolean"][i];
							if (i < robotMem.memory["boolean"].Count - 1)
								valueBool = valueBool + ", ";
						}
						valueBool = valueBool + "\n";
					}

					string valueString = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("string")){
						valueString = valueString + "string : ";
						for (int i = 0; i < robotMem.memory["string"].Count; i++){
							valueString = valueString + robotMem.memory["string"][i];
							if (i < robotMem.memory["string"].Count - 1)
								valueString = valueString + ", ";
						}
					}
					
					tooltipContent.text = $"#agentName<br>clique pour voir mon<br>comportement !\n\nMémoire :\n{valueInt}{valueBool}{valueString}";
				}
				break;
			case BasicAction.ActionType.VarBool:
				//Add int variable processsing
				if (ca.agent.GetComponent<robotMemory>())
				{
					// check si variable déifni
					string s;
					if (ca.GetComponentInChildren<TMP_InputField>().text == "")
					{
						s = "True";
						Debug.Log("string not init " + s);
					}
					else
					{
						s = ca.transform.GetComponentInChildren<TMP_InputField>().text;
						Debug.Log("Value found : " + s);
					}
					// check si type bool existe déjà dans la mémoire
					if (!ca.agent.GetComponent<robotMemory>().memory.ContainsKey("boolean"))
					{
						Debug.Log("Not found in memo");
						List<string> ls = new List<string>();	
						ls.Add(s);
						Debug.Log("Added variable boolean of value " + s);
						ca.agent.GetComponent<robotMemory>().memory.Add("boolean", ls);
					}
					else{
						Debug.Log("Found in memo");
						List<string> ls = new List<string>();
						ls.Add(s);
						ca.agent.GetComponent<robotMemory>().memory["boolean"] = ls;
						Debug.Log("Added variable string of value " + s);
					}
					
					// tooltip
					TooltipContent tooltipContent = ca.agent.GetComponentInChildren<TooltipContent>();
					robotMemory robotMem = ca.agent.GetComponent<robotMemory>();
					
					string valueInt = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("int")){
						valueInt = valueInt + "int : ";
						for (int i = 0; i < robotMem.memory["int"].Count; i++){
							valueInt = valueInt + robotMem.memory["int"][i];
							if (i < robotMem.memory["int"].Count - 1)
								valueInt = valueInt + ", ";
						}
						valueInt = valueInt + "\n";
					}

					string valueBool = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("boolean")){
						valueBool = valueBool + "boolean : ";
						for (int i = 0; i < robotMem.memory["boolean"].Count; i++){
							valueBool = valueBool + robotMem.memory["boolean"][i];
							if (i < robotMem.memory["boolean"].Count - 1)
								valueBool = valueBool + ", ";
						}
						valueBool = valueBool + "\n";
					}

					string valueString = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("string")){
						valueString = valueString + "string : ";
						for (int i = 0; i < robotMem.memory["string"].Count; i++){
							valueString = valueString + robotMem.memory["string"][i];
							if (i < robotMem.memory["string"].Count - 1)
								valueString = valueString + ", ";
						}
					}
					
					tooltipContent.text = $"#agentName<br>clique pour voir mon<br>comportement !\n\nMémoire :\n{valueInt}{valueBool}{valueString}";
				}
				break;
			case BasicAction.ActionType.VarString:
				//Add int variable processsing
				if (ca.agent.GetComponent<robotMemory>())
				{
					// check si variable déifni
					string s;
					if (ca.GetComponentInChildren<TMP_InputField>().text == "")
					{
						s = "";
						Debug.Log("string not init " + s);
					}
					else
					{
						s = ca.transform.GetComponentInChildren<TMP_InputField>().text;
						Debug.Log("Value found : " + s);
					}
					// check si type string existe déjà dans la mémoire
					if (!ca.agent.GetComponent<robotMemory>().memory.ContainsKey("string"))
					{
						Debug.Log("Type string not found in memo");
						List<string> ls = new List<string>();	
						ls.Add(s);
						Debug.Log("Added variable string of value " + s);
						ca.agent.GetComponent<robotMemory>().memory.Add("string", ls);
					}
					else{
						Debug.Log("Type string found in memo");
						// List<string> ls = ca.agent.GetComponent<robotMemory>().memory["string"];
						// ls.Add(s);
						ca.agent.GetComponent<robotMemory>().memory["string"].Add(s);
						Debug.Log("Added variable string of value " + s);
					
					}

					// tooltip
					TooltipContent tooltipContent = ca.agent.GetComponentInChildren<TooltipContent>();
					robotMemory robotMem = ca.agent.GetComponent<robotMemory>();
					
					string valueInt = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("int")){
						valueInt = valueInt + "int : ";
						for (int i = 0; i < robotMem.memory["int"].Count; i++){
							valueInt = valueInt + robotMem.memory["int"][i];
							if (i < robotMem.memory["int"].Count - 1)
								valueInt = valueInt + ", ";
						}
						valueInt = valueInt + "\n";
					}

					string valueBool = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("boolean")){
						valueBool = valueBool + "boolean : ";
						for (int i = 0; i < robotMem.memory["boolean"].Count; i++){
							valueBool = valueBool + robotMem.memory["boolean"][i];
							if (i < robotMem.memory["boolean"].Count - 1)
								valueBool = valueBool + ", ";
						}
						valueBool = valueBool + "\n";
					}

					string valueString = "";
					if (ca.agent.GetComponent<robotMemory>().memory.ContainsKey("string")){
						valueString = valueString + "string : ";
						for (int i = 0; i < robotMem.memory["string"].Count; i++){
							valueString = valueString + robotMem.memory["string"][i];
							if (i < robotMem.memory["string"].Count - 1)
								valueString = valueString + ", ";
						}
					}
					
					tooltipContent.text = $"#agentName<br>clique pour voir mon<br>comportement !\n\nMémoire :\n{valueInt}{valueBool}{valueString}";
				}
				break;	
			
			case BasicAction.ActionType.Activate:
				Position agentPos = ca.agent.GetComponent<Position>();
				foreach ( GameObject actGo in f_activableConsole){
					if(actGo.GetComponent<Position>().x == agentPos.x && actGo.GetComponent<Position>().y == agentPos.y){
						actGo.GetComponent<AudioSource>().Play();
						//Ajouter ici le check porte avec variable + vérif de la condition
						// toggle activable GameObject
						PanelMemory panelMemory = actGo.GetComponent<PanelMemory>();
						Debug.Log("[onCurrentAction] panelMemory.value : "+panelMemory.value);
						if (panelMemory.value == ""){
							Debug.Log("[onCurrentAction] panelMemory.value null : "+panelMemory.value);
							if (actGo.GetComponent<TurnedOn>())
								GameObjectManager.removeComponent<TurnedOn>(actGo);
							else
								GameObjectManager.addComponent<TurnedOn>(actGo);
						}
						else{
							Dictionary<int, string> varTypeEnum = new Dictionary<int, string>()
							{
								{ 0, "int" },
								{ 1, "boolean" },
								{ 2, "string" },
							};
							Debug.Log("[onCurrentAction] panelMemory.type : "+panelMemory.type);
							Dictionary<string, List<string>> robotMemory = ca.agent.GetComponent<robotMemory>().memory;
							Debug.Log("[onCurrentAction] containsKeys : "+robotMemory.ContainsKey(varTypeEnum[panelMemory.type]));
							if (robotMemory.ContainsKey(varTypeEnum[panelMemory.type])){
								bool flag = false;
								Debug.Log("[OnCurrentAction] robotMemory has "+robotMemory[varTypeEnum[panelMemory.type]].Count+" elements");
								foreach (string value in robotMemory[varTypeEnum[panelMemory.type]])
								{
									Debug.Log("[onCurrentAction] robotMemory.value : "+value);
									if (string.Compare(value, panelMemory.value) == 0){
										Debug.Log("[OnCurrentAction] value = "+value+", panelMemory.value = "+panelMemory.value);
										flag = true;
										break;
									}
								}

								if (flag){
									if (actGo.GetComponent<TurnedOn>())
										GameObjectManager.removeComponent<TurnedOn>(actGo);
									else
										GameObjectManager.addComponent<TurnedOn>(actGo);
								}
							}
							else{
								Debug.Log("[onCurrentAction] varType inconnu : "+panelMemory.type+" -> "+varTypeEnum[panelMemory.type]);
								string keys = "";
								foreach (var key in robotMemory.Keys)
								{
									keys = keys + key + " ";
								}
								Debug.Log("[onCurrentAction] robotMemory Keys : "+keys);
							}
						}
						// Debug.Log("[CurrentActionExecutor][onNewCurrentAction] panel memory : type = "+actGo.GetComponent<PanelMemory>().type.ToString());
						// Debug.Log("[CurrentActionExecutor][onNewCurrentAction] panel memory : value = "+actGo.GetComponent<PanelMemory>().value);
					}
				}
				ca.agent.GetComponent<Animator>().SetTrigger("Action");
				break;
		}
		ca.StopAllCoroutines();
		if (ca.gameObject.activeInHierarchy)
			ca.StartCoroutine(Utility.pulseItem(ca.gameObject));
		// notify agent moving
		if (ca.agent.CompareTag("Drone") && !ca.agent.GetComponent<Moved>())
			GameObjectManager.addComponent<Moved>(ca.agent);
	}

	private void ApplyForward(GameObject go){
		Position pos = go.GetComponent<Position>();
		switch (go.GetComponent<Direction>().direction){
			case Direction.Dir.North:
				if (!checkObstacle(pos.x, pos.y - 1))
				{
					pos.targetX = pos.x;
					pos.targetY = pos.y - 1;
				}
				else
					GameObjectManager.addComponent<ForceMoveAnimation>(go);
				break;
			case Direction.Dir.South:
				if(!checkObstacle(pos.x,pos.y + 1)){
					pos.targetX = pos.x;
					pos.targetY = pos.y + 1;
				}
				else
					GameObjectManager.addComponent<ForceMoveAnimation>(go);
				break;
			case Direction.Dir.East:
				if(!checkObstacle(pos.x + 1, pos.y)){
					pos.targetX = pos.x + 1;
					pos.targetY = pos.y;
				}
				else
					GameObjectManager.addComponent<ForceMoveAnimation>(go);
				break;
			case Direction.Dir.West:
				if(!checkObstacle(pos.x - 1, pos.y)){
					pos.targetX = pos.x - 1;
					pos.targetY = pos.y;
				}
				else
					GameObjectManager.addComponent<ForceMoveAnimation>(go);
				break;
		}
	}

	private void ApplyTurnLeft(GameObject go){
		switch (go.GetComponent<Direction>().direction){
			case Direction.Dir.North:
				go.GetComponent<Direction>().direction = Direction.Dir.West;
				break;
			case Direction.Dir.South:
				go.GetComponent<Direction>().direction = Direction.Dir.East;
				break;
			case Direction.Dir.East:
				go.GetComponent<Direction>().direction = Direction.Dir.North;
				break;
			case Direction.Dir.West:
				go.GetComponent<Direction>().direction = Direction.Dir.South;
				break;
		}
	}

	private void ApplyTurnRight(GameObject go){
		switch (go.GetComponent<Direction>().direction){
			case Direction.Dir.North:
				go.GetComponent<Direction>().direction = Direction.Dir.East;
				break;
			case Direction.Dir.South:
				go.GetComponent<Direction>().direction = Direction.Dir.West;
				break;
			case Direction.Dir.East:
				go.GetComponent<Direction>().direction = Direction.Dir.South;
				break;
			case Direction.Dir.West:
				go.GetComponent<Direction>().direction = Direction.Dir.North;
				break;
		}
	}

	private void ApplyTurnBack(GameObject go){
		switch (go.GetComponent<Direction>().direction){
			case Direction.Dir.North:
				go.GetComponent<Direction>().direction = Direction.Dir.South;
				break;
			case Direction.Dir.South:
				go.GetComponent<Direction>().direction = Direction.Dir.North;
				break;
			case Direction.Dir.East:
				go.GetComponent<Direction>().direction = Direction.Dir.West;
				break;
			case Direction.Dir.West:
				go.GetComponent<Direction>().direction = Direction.Dir.East;
				break;
		}
	}

	private bool checkObstacle(int x, int z){
		foreach( GameObject go in f_wall){
			if(go.GetComponent<Position>().x == x && go.GetComponent<Position>().y == z)
				return true;
		}
		return false;
	}
}
