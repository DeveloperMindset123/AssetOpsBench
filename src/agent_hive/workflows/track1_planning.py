from agent_hive.task import Task
from pydantic import Field
from typing import List
from agent_hive.enum import ContextType
import json
from agent_hive.workflows.base_workflow import Workflow
from reactxen.utils.model_inference import watsonx_llm
import re
from agent_hive.workflows.sequential import SequentialWorkflow
from agent_hive.agents.plan_reviewer_agent import PlanReviewerAgent
from agent_hive.logger import get_custom_logger

logger = get_custom_logger(__name__)


class NewPlanningWorkflow(Workflow):
    """
    Participant Template for Planning Review Workflow.
    ---------------------------------------------------
    📝 Instructions for participants:
    - Only modify the section marked with "TODO: Edit prompt here"
    - Do NOT change any workflow logic, agents, or execution components
    - Keep all retry, memory, and sequential execution intact
    """

    llm: str = Field(description="LLM used by the task planning.")

    def __init__(self, tasks: List[Task], llm: str):
        self.tasks = tasks
        self.memory = []
        self.max_memory = 10
        self.llm = llm
        self.max_retries = 5
        self._verify_tasks()

    def _verify_tasks(self):
        if not isinstance(self.tasks, list):
            raise ValueError("tasks must be a list of Task objects")
        if len(self.tasks) != 1:
            raise ValueError("Planning only supports one task")
        task = self.tasks[0]
        if task.agents is None or len(task.agents) < 1:
            raise ValueError("Task must have at least one agent")

    def run(self, enable_summarization=False):
        generated_steps = self.generate_steps()

        sequential_workflow = SequentialWorkflow(
            tasks=generated_steps, context_type=ContextType.SELECTED
        )

        return sequential_workflow.run()

    def generate_steps(self, save_plan=False, saved_plan_filename=""):
        task = self.tasks[0]
        agent_descriptions = ""

        # =========================================================
        # TODO: Participants can edit this section ONLY
        # 🎨 Purpose: Customize how agent information is collected and formatted
        # ✅ Allowed: 
        #     - Change numbering style or bullet points
        #     - Include additional metadata (e.g., agent capabilities, tags)
        #     - Provide examples in a different format
        #     - Add emojis or formatting to make the prompt clearer 
        #     - More thinking
        # ❌ Not allowed: 
        #     - Modify workflow execution
        #     - Replace the base ReAct agent or Executor
        #     - Change memory or retry logic
        # =========================================================

        agent_descriptions += "\n🎯 **AVAILABLE AGENTS & THEIR SPECIALIZED CAPABILITIES:**\n"
        
        for ii, aagent in enumerate(task.agents):
            # Enhanced agent formatting with clear capability mapping
            agent_descriptions += f"\n🔧 **AGENT {ii + 1}: {aagent.name.upper()}**"
            agent_descriptions += f"\n   📋 Description: {aagent.description}"
            
            # Add capability tags based on agent name patterns
            if "IoT" in aagent.name or "iot" in aagent.name.lower():
                agent_descriptions += f"\n   🏷️ Specializations: [DATA_RETRIEVAL, ASSET_DISCOVERY, SENSOR_METADATA, HISTORICAL_DATA]"
                agent_descriptions += f"\n   💡 Best for: Finding sites, assets, downloading sensor data, retrieving metadata"
            elif "Failure" in aagent.name or "FMSR" in aagent.name:
                agent_descriptions += f"\n   🏷️ Specializations: [FAILURE_ANALYSIS, SENSOR_MAPPING, MAINTENANCE_INSIGHTS]"
                agent_descriptions += f"\n   💡 Best for: Identifying failure modes, mapping sensors to failures, maintenance recommendations"
            
            # Enhanced task examples with context
            if "task_examples" in aagent.__dict__ and aagent.task_examples:
                agent_descriptions += f"\n   📚 **Proven Use Cases:**"
                for idx, task_example in enumerate(aagent.task_examples[:3], start=1):  # Limit to top 3 examples
                    agent_descriptions += f"\n      {idx}. {task_example}"
                if len(aagent.task_examples) > 3:
                    agent_descriptions += f"\n      ... and {len(aagent.task_examples) - 3} more capabilities"
            
            # Add tool-based capability hints
            if hasattr(aagent, 'tools') and aagent.tools:
                tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in aagent.tools]
                agent_descriptions += f"\n   🛠️ Tools Available: {', '.join(tool_names[:3])}"
                if len(tool_names) > 3:
                    agent_descriptions += f" (+{len(tool_names) - 3} more)"
            
            agent_descriptions += "\n"

        # =========================================================
        # END OF EDITABLE SECTION
        # 🚫 Participants should not modify code below this line
        # ❌ No new variables, functions, or workflow logic allowed
        # ✅ Only modify the section marked as TODO above
        # =========================================================

        prompt = self.get_prompt(task.description, agent_descriptions)
        logger.info(f"Plan Generation Prompt: \n{prompt}")
        llm_response = watsonx_llm(
            prompt, model_id=self.llm,
        )["generated_text"]
        logger.info(f"Plan: \n{llm_response}")

        final_plan = llm_response
        self.memory = []

        task_pattern = r"#Task\d+: (.+)"
        agent_pattern = r"#Agent\d+: (.+)"
        dependency_pattern = r"#Dependency\d+: (.+)"
        output_pattern = r"#ExpectedOutput\d+: (.+)"

        tasks = re.findall(task_pattern, final_plan)
        agents = re.findall(agent_pattern, final_plan)
        dependencies = re.findall(dependency_pattern, final_plan)
        outputs = re.findall(output_pattern, final_plan)

        if save_plan:
            if not saved_plan_filename.endswith(".txt"):
                saved_plan_filename += ".txt"

            saved_plan_text = f"Question: {task.description}\nPlan:\n{final_plan}"
            with open(saved_plan_filename, "w") as f:
                f.write(saved_plan_text)

        planned_tasks = []
        for i in range(len(tasks)):
            task_description = tasks[i]
            if i == len(agents):
                break
            agent_name = agents[i]
            if i < len(dependencies):
                dependency = dependencies[i]
            else:
                dependency = "None"
            if i < len(outputs):
                expected_output = outputs[i]
            else:
                expected_output = ""

            selected_agent = None
            for agent in task.agents:
                if agent.name == agent_name:
                    selected_agent = agent
                    break
            if selected_agent is None:
                selected_agent = task.agents[0]

            if dependency != "None":
                numbers = re.findall(r"#S(\d+)", dependency)
                numbers = list(map(int, numbers))
                context = [planned_tasks[i - 1] for i in numbers]
            else:
                context = []

            a_task = Task(
                description=task_description,
                expected_output=expected_output,
                agents=[selected_agent],
                context=context,
            )
            planned_tasks.append(a_task)

        logger.info(f"Planned Tasks: \n{planned_tasks}")

        return planned_tasks

    def get_prompt(self, task_description, agent_descriptions):
        # =========================================================
        # TODO: Participants can edit this section ONLY
        # 🎨 Purpose: Improve prompt clarity, formatting, emojis, guidance
        # ✅ Allowed: Wording, structure, examples, emojis
        # ❌ Not allowed: Changing workflow, ReAct agent, Executor, or memory logic
        # =========================================================

        prompt = f"""
🎯 **EXPERT TASK PLANNER** - Create an optimal step-by-step execution plan

**Your Mission:** Analyze the problem and create a strategic plan using the specialized agents below.

🧠 **PLANNING STRATEGY:**
1. **Identify the core task type** - Is this data retrieval, analysis, or both?
2. **Choose the right agent sequence** - Start with data gathering (IoT), then analysis (FMSR)
3. **Minimize steps** - Aim for 2-4 steps maximum for efficiency
4. **Ensure data flow** - Each step should build upon previous results

⚡ **CRITICAL RULES:**
- ✅ Use ONLY the agents provided below
- ✅ Maximum 4 steps (prefer 2-3 for simple tasks)
- ✅ Each step must have: Task, Agent, Dependency, ExpectedOutput
- ✅ Make tasks specific and actionable
- ✅ Use proper dependency references (#S1, #S2, etc.)

📋 **REQUIRED FORMAT:**
```
#Task1: <Specific, actionable task description>
#Agent1: <exact_agent_name_from_list>
#Dependency1: None
#ExpectedOutput1: <Clear description of expected result>

#Task2: <Next specific task>
#Agent2: <exact_agent_name_from_list>
#Dependency2: #S1
#ExpectedOutput2: <Clear description of expected result>
```

{agent_descriptions}

🎯 **PROBLEM TO SOLVE:**
{task_description}

💡 **PLANNING TIPS:**
- For data queries: Start with IoT agent to gather information
- For analysis: Use FMSR agent with IoT data as input
- Keep tasks focused and specific
- Ensure each step has a clear, measurable output

**Your optimized plan:**
"""
        # =========================================================
        # End of participant editable section
        # =========================================================
        return prompt
