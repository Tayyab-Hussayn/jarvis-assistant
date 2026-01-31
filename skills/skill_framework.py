"""
Skills Framework - Advanced capabilities and domain expertise
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class SkillResult:
    success: bool
    output: Any
    confidence: float
    reasoning: str

class BaseSkill(ABC):
    """Base class for all skills"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        pass

class PromptOptimizer(BaseSkill):
    """Optimize prompts for different tasks"""
    
    def __init__(self):
        super().__init__("prompt_optimizer")
        self.templates = {
            "coding": "You are an expert programmer. {task}. Provide clean, efficient code.",
            "analysis": "Analyze the following: {task}. Provide structured insights.",
            "planning": "Create a detailed plan for: {task}. Include steps and timeline."
        }
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        task_type = context.get("type", "general")
        task = context.get("task", "")
        
        template = self.templates.get(task_type, "Complete this task: {task}")
        optimized_prompt = template.format(task=task)
        
        return SkillResult(
            success=True,
            output=optimized_prompt,
            confidence=0.9,
            reasoning=f"Applied {task_type} template"
        )

class ArchitectureDesigner(BaseSkill):
    """Design software architecture"""
    
    def __init__(self):
        super().__init__("architecture_designer")
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        project_type = context.get("project_type", "web_app")
        requirements = context.get("requirements", [])
        
        if project_type == "web_app":
            architecture = {
                "frontend": "React/Vue.js",
                "backend": "Node.js/Python",
                "database": "PostgreSQL",
                "deployment": "Docker + Cloud"
            }
        else:
            architecture = {
                "structure": "Modular design",
                "patterns": "MVC/Clean Architecture",
                "testing": "Unit + Integration tests"
            }
        
        return SkillResult(
            success=True,
            output=architecture,
            confidence=0.8,
            reasoning=f"Standard {project_type} architecture"
        )

class CodeGenerator(BaseSkill):
    """Generate code following best practices"""
    
    def __init__(self):
        super().__init__("code_generator")
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        language = context.get("language", "python")
        task = context.get("task", "")
        
        if "hello world" in task.lower():
            if language == "python":
                code = 'print("Hello, World!")'
            elif language == "javascript":
                code = 'console.log("Hello, World!");'
            else:
                code = f'// Hello World in {language}\n// Implementation needed'
        else:
            code = f"# {task}\n# Implementation needed for {language}"
        
        return SkillResult(
            success=True,
            output=code,
            confidence=0.7,
            reasoning=f"Generated {language} code for: {task}"
        )

class SelfImprovement(BaseSkill):
    """Learn from execution outcomes"""
    
    def __init__(self):
        super().__init__("self_improvement")
        self.patterns = {}
    
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        outcome = context.get("outcome", {})
        task_type = context.get("task_type", "unknown")
        
        # Simple pattern learning
        if task_type not in self.patterns:
            self.patterns[task_type] = {"successes": 0, "failures": 0}
        
        if outcome.get("success", False):
            self.patterns[task_type]["successes"] += 1
        else:
            self.patterns[task_type]["failures"] += 1
        
        success_rate = self.patterns[task_type]["successes"] / (
            self.patterns[task_type]["successes"] + self.patterns[task_type]["failures"]
        )
        
        return SkillResult(
            success=True,
            output={"success_rate": success_rate, "patterns": self.patterns},
            confidence=0.9,
            reasoning=f"Updated patterns for {task_type}"
        )

class SkillRegistry:
    """Registry for all skills"""
    
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self._register_default_skills()
    
    def _register_default_skills(self):
        """Register default skills"""
        skills = [
            PromptOptimizer(),
            ArchitectureDesigner(),
            CodeGenerator(),
            SelfImprovement()
        ]
        
        for skill in skills:
            self.skills[skill.name] = skill
    
    def get_skill(self, name: str) -> BaseSkill:
        """Get skill by name"""
        return self.skills.get(name)
    
    async def execute_skill(self, name: str, context: Dict[str, Any]) -> SkillResult:
        """Execute a skill"""
        skill = self.get_skill(name)
        if not skill:
            return SkillResult(
                success=False,
                output=None,
                confidence=0.0,
                reasoning=f"Skill {name} not found"
            )
        
        return await skill.execute(context)

# Global skill registry
skill_registry = SkillRegistry()
