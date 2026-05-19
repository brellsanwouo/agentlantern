# Quick Start: No LLM Required

## Fastest Way to Test AgentLantern

Follow this guide to create and test a minimal CrewAI project **without needing any LLM or API keys**.

## Step 1: Install CrewAI

```bash
pip install crewai
```

## Step 2: Create a Simple Project

```bash
crewai create my_test_project
cd my_test_project
```

## Step 3: Modify agents.yaml (No API Keys Needed)

Edit `src/my_test_project/config/agents.yaml`:

```yaml
researcher:
  role: Data Researcher
  goal: Research and analyze topics
  backstory: You are an expert at finding and analyzing information.
  tools: []
  verbose: true

writer:
  role: Content Writer
  goal: Write high quality content
  backstory: You are an excellent writer who creates engaging content.
  tools: []
  verbose: true

analyst:
  role: Data Analyst
  goal: Analyze and interpret data
  backstory: You are skilled at analyzing patterns and insights.
  tools: []
  verbose: true
```

## Step 4: Modify tasks.yaml

Edit `src/my_test_project/config/tasks.yaml`:

```yaml
research_task:
  description: Research the topic thoroughly
  expected_output: Comprehensive research document
  agent: researcher

writing_task:
  description: Write an article based on research
  expected_output: Well-written article
  agent: writer
  
analysis_task:
  description: Analyze the written content
  expected_output: Analysis report
  agent: analyst
```

## Step 5: Modify crew.py

Edit `src/my_test_project/crew.py` - remove LLM initialization:

```python
from crewai import Agent, Task, Crew

class MyTestProjectCrew:
    """Your test crew implementation without LLM"""

    def __init__(self):
        """Initialize the crew without LLM dependencies"""
        pass

    def setup_agents(self):
        """Setup agents (no LLM calls)"""
        self.researcher = Agent(
            role="Data Researcher",
            goal="Research topics",
            backstory="Expert researcher",
            verbose=True,
            allow_delegation=False
        )

        self.writer = Agent(
            role="Content Writer",
            goal="Write content",
            backstory="Expert writer",
            verbose=True,
            allow_delegation=False
        )

        self.analyst = Agent(
            role="Data Analyst",
            goal="Analyze data",
            backstory="Expert analyst",
            verbose=True,
            allow_delegation=False
        )

    def setup_tasks(self):
        """Setup tasks"""
        self.research_task = Task(
            description="Research the topic",
            expected_output="Research document",
            agent=self.researcher
        )

        self.writing_task = Task(
            description="Write article",
            expected_output="Article",
            agent=self.writer
        )

        self.analysis_task = Task(
            description="Analyze content",
            expected_output="Analysis",
            agent=self.analyst
        )

    def crew(self) -> Crew:
        """Create the crew"""
        self.setup_agents()
        self.setup_tasks()

        return Crew(
            agents=[self.researcher, self.writer, self.analyst],
            tasks=[self.research_task, self.writing_task, self.analysis_task],
            verbose=True
        )
```

## Step 6: Install AgentLantern

```bash
pip install agentlantern
```

## Step 7: Generate Documentation

```bash
# From your project root
lantern docs
```

You should see:
```
Generated AgentLantern docs for my_test_project
- /path/to/project/docs/overview.md
- /path/to/project/docs/architecture.md
- /path/to/project/docs/agents.md
- /path/to/project/docs/tasks.md
- ... and more
```

## Step 8: View Documentation

```bash
lantern web
```

Open your browser to `http://localhost:8000` and explore:
- **Agents** - See your three agents (Researcher, Writer, Analyst)
- **Tasks** - See your three tasks with dependencies
- **Architecture** - Visual overview of your crew
- **Runbook** - How to execute your crew

## What You Just Did

✅ Created a minimal CrewAI project  
✅ Defined agents and tasks (no LLM needed)  
✅ Generated documentation with AgentLantern  
✅ Viewed beautiful documentation locally  

## That's It!

No API keys, no LLM setup, no complex configuration. You now have working documentation for a CrewAI project.

## Next Steps

- [Learn Usage Patterns](usage.md)
- [Explore Examples](examples.md)
- [Check API Reference](api.md)
- Add more agents and tasks to your project
- Explore the generated documentation files
- Try deploying to GitHub Pages

## Tips

- You can have as many agents and tasks as you want
- No LLM = no costs
- Perfect for testing and learning
- Documentation generates instantly
- Export docs anywhere - no dependencies needed
