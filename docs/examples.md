# Examples

## Example 1: Document an Energy Analysis Agent

```bash
# Clone the example project
git clone https://github.com/brellsanwouo/agent-energy-consumption.git
cd agent-energy-consumption

# Generate documentation
lantern docs

# View it
lantern web
```

The documentation will show:
- **Agents**: Energy Analysis Agent, Data Processing Agent
- **Tasks**: Energy collection, analysis, reporting
- **Architecture**: Multi-agent system for energy monitoring
- **Workflow**: Data flow from collection to reporting

## Example 2: Document Multiple Projects

Run documentation generation for multiple CrewAI projects:

```bash
# Project A
lantern docs ~/projects/project-a

# Project B  
lantern docs ~/projects/project-b

# Project C
lantern docs ~/projects/project-c
```

## Example 3: View Multiple Documentation Sites

View documentation for different projects on different ports:

**Terminal 1:**
```bash
lantern web ~/projects/project-a --port 9000
# Visit http://localhost:9000
```

**Terminal 2:**
```bash
lantern web ~/projects/project-b --port 9001
# Visit http://localhost:9001
```

**Terminal 3:**
```bash
lantern web ~/projects/project-c --port 9002
# Visit http://localhost:9002
```

## Example 4: CI/CD Integration

Generate docs automatically when pushing to GitHub:

```yaml
# .github/workflows/docs.yml
name: Generate Docs

on: [push]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
      - run: lantern docs
      - uses: actions/upload-artifact@v2
        with:
          name: documentation
          path: docs/
```

## Example 5: Deploying to GitHub Pages

1. Generate docs locally:
```bash
lantern docs
```

2. Commit and push:
```bash
git add docs/
git commit -m "Update documentation"
git push
```

3. Configure GitHub Pages in repository settings:
   - Source: `main` branch
   - Folder: `/docs`

Your docs are now live at: `https://username.github.io/project-name/`

## Example 6: Docker Deployment

Create a Dockerfile to serve documentation:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"

RUN lantern docs

CMD ["lantern", "web", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t crew-docs .
docker run -p 9000:9000 crew-docs
```

## Example 7: Customize Port for Development

While developing, use different ports for different iterations:

```bash
# First version
lantern web --port 9000

# Make changes to crew.py
# Regenerate docs
lantern docs

# View updated docs
lantern web --port 9001
```

## Example 8: Share Static Documentation

After generating docs, share the `docs/` folder:

```bash
# Zip the documentation
zip -r crew-documentation.zip docs/

# Share crew-documentation.zip
# Recipient can:
# 1. Extract the zip
# 2. Open docs/index.html in browser
# Or serve the extracted docs folder with any static web server.
```

## Common Workflows

### Development Workflow
```bash
# 1. Create/modify your CrewAI project
# 2. Generate updated docs
lantern docs

# 3. Check the output
lantern web

# 4. Make changes if needed
# 5. Regenerate and refresh browser
```

### Documentation Review
```bash
# Generate docs for a specific branch
git checkout feature/new-agents
lantern docs

# Review on port 9000
lantern web --port 9000

# Switch to another branch
git checkout main
lantern docs

# Review on port 9001
lantern web --port 9001

# Compare both versions side-by-side
```

### Team Collaboration
```bash
# Generate docs
lantern docs

# Commit to GitHub
git add docs/
git commit -m "Update docs for new features"
git push

# Team members pull and review
git pull
lantern web

# Discuss changes
# Make improvements
# Repeat
```

## Troubleshooting Examples

### Problem: Documentation not updating

Solution:
```bash
# Remove old docs and regenerate
rm -rf docs/
lantern docs
lantern web
```

### Problem: Port 9000 is busy

Solution:
```bash
lantern web --port 9001
# Or find what's using 9000
lsof -i :9000
```

### Problem: Can't find project

Solution:
```bash
# Check project structure
ls src/your_project/config/

# Make sure files exist:
# - src/your_project/crew.py
# - src/your_project/config/agents.yaml
# - src/your_project/config/tasks.yaml
```

## Next Steps

- [Check API Reference](api.md)
- [View FAQ](faq.md)
- [Back to Guide](guide.md)
