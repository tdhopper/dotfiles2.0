# 🛠️ Skill Builder for Claude Code

> **The meta-skill that builds skills!** 🎯

Transform your Claude Code CLI experience by creating, editing, and converting skills like a pro. Because let's face it—Claude Code doesn't have an interactive skill builder yet, but now **you do**! 🚀

Built on Anthropic's innovative [Agent Skills architecture](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), this skill demonstrates how to extend Claude's capabilities in practical, production-ready ways.

---

## 🎪 What Is This?

**Skill Builder** is a specialized Claude Code skill that acts as your personal guide for mastering the Skills system. Think of it as a skill that teaches Claude how to build more skills. Meta? Absolutely. Powerful? You bet! 💪

Created by [**Ken Collins**](https://github.com/metaskills/) (AWS Serverless Hero & VP of Product at Randstad Digital), this skill embodies years of practical AI engineering experience. Check out more AI insights and practical guides at [**Unremarkable AI**](https://www.unremarkable.ai/about/) 🧠

## 🧪 An Experiment in General-Purpose Skills

This is **an experiment** in using Claude Code for **more general-purpose use cases** beyond typical per-project workflows. While most Claude Code skills are project-specific, Skill Builder demonstrates how skills can work **system-wide** across all your projects.

**This means you should personalize it!** 🎨

The version here reflects Ken's workflow—heavy on CLI tools (gh, aws, npm), Node.js scripting, and system-wide automation. Your needs might be different:
- Maybe you prefer Python over Node.js
- Perhaps you work with different cloud providers
- Your CLI toolkit might include different tools
- Your naming conventions might vary

**Fork it, customize it, make it yours!** The beauty of skills is they can be tailored to your individual development style and the tools you actually use every day.

---

## ✨ Three Superpowers in One Skill

### 🎨 1. Create New Skills from Scratch
Build production-ready Claude Code skills with:
- ✅ Perfect YAML frontmatter
- ✅ Invocation-optimized descriptions
- ✅ CLI-first approach (gh, aws, npm, and more!)
- ✅ Modern Node.js patterns (ESM imports, v24+)
- ✅ Intention-revealing file names
- ✅ Progressive disclosure architecture

### ✏️ 2. Edit & Refine Existing Skills
Level up your skills with:
- 🎯 Better descriptions for improved invocation
- 📚 Progressive disclosure (keep SKILL.md under 500 lines)
- 🔧 CLI and Node.js best practices
- 📂 Organized multi-file structures

### 🔄 3. Convert Sub-Agents to Skills
Migrate your Claude Code sub-agents to the Skills format:
- 🧬 Transform agent configs to skill format
- 🏷️ Convert names to gerund form (`processing-data` not `data-processor`)
- 🎪 Enhance descriptions with invocation triggers
- 🚫 Remove agent-specific fields (model, tools)
- 📦 Preserve domain expertise and examples

---

## 🚀 One-Line Installation

```bash
git clone https://github.com/metaskills/skill-builder.git ~/.claude/skills/skill-builder
```

That's it! 🎉 The skill is now globally available across all your Claude Code projects.

---

## 💡 How to Use

Once installed, simply ask Claude Code natural questions like:

**Creating New Skills:**
```
"Help me create a skill for deploying AWS Lambda functions"
"I need a skill for processing GitHub webhooks"
"Build a skill for analyzing CloudFormation templates"
```

**Editing Skills:**
```
"Improve the description for my data-processing skill"
"Help me organize my skill with progressive disclosure"
"Add CLI examples to my existing skill"
```

**Converting Sub-Agents:**
```
"Convert my code-reviewer sub-agent to a skill"
"Transform my debugging sub-agent into a skill"
```

The Skill Builder will:
1. 🔍 Reference the latest official documentation
2. 🤔 Ask clarifying questions to understand your needs
3. 🎯 Guide you through the process step-by-step
4. ✨ Create production-ready, well-structured skills

---

## 🎯 Why Use Skill Builder?

### 📚 Always Up-to-Date
- Automatically references [official Anthropic documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- Stays current with [best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- Implements patterns from [Anthropic's engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 🎨 Opinionated & Practical
- CLI-first mindset (gh, aws, npm, jq, etc.)
- Node.js v24+ with ESM imports (no Python!)
- Gerund-form naming conventions
- Intention-revealing file names
- Progressive disclosure for context efficiency

### 🚀 Production-Ready Output
- Proper YAML frontmatter
- Invocation-optimized descriptions
- Complete, runnable examples
- Validation checklists
- Troubleshooting guides

---

## 📖 What's Inside

```
skill-builder/
├── SKILL.md                              # Core skill instructions
├── converting-sub-agents-to-skills.md    # Comprehensive conversion guide
└── templates/
    └── skill-template.md                 # Template for new skills
```

Each file is meticulously crafted with:
- 🎯 Clear, actionable instructions
- 💻 Complete code examples (Node.js + CLI)
- 📊 Real-world use cases from official docs
- ✅ Validation and testing guidelines

---

## 🌟 Features That Make You Smile

- **🤖 Meta AF**: A skill that teaches Claude to build skills
- **📝 Comprehensive**: 900+ lines of curated guidance
- **🎨 CLI-Focused**: Leverage gh, aws, npm, and modern tooling
- **⚡ Node.js Native**: ESM imports, modern JavaScript patterns
- **📚 Doc-Driven**: Always references latest official resources
- **🎯 Invocation-Optimized**: Descriptions that actually trigger properly
- **🔧 Battle-Tested**: Patterns from real-world AI engineering

---

## 🙏 About the Creator

Built with ❤️ by [**Ken Collins**](https://github.com/metaskills/)

Ken is an AWS Serverless Hero, VP of Product at Randstad Digital + Torc, and former Principal Engineer at Custom Ink. He's passionate about practical AI applications, serverless architectures, and making complex systems approachable.

**Learn More:**
- 🐙 GitHub: [@metaskills](https://github.com/metaskills/)
- 📝 Blog: [Unremarkable AI](https://www.unremarkable.ai/about/)
- 🎯 Focus: Practical AI that solves real-world problems

---

## 🤝 Contributing

Found a way to make this skill even better? PRs are welcome! 🎉

This skill follows the philosophy: "Challenge every piece of information—Does Claude really need this explanation?"

---

## 📜 License

MIT License - Use it, share it, build amazing things! 🚀

---

## 🎬 Get Started Now!

```bash
# Install the skill
git clone https://github.com/metaskills/skill-builder.git ~/.claude/skills/skill-builder

# Start building
# Just open Claude Code and ask:
# "Help me create a skill for..."
```

**Happy skill building!** 🛠️✨

---

*Made with 🧠 and ☕ by humans who believe AI should be practical, not mystical.*
