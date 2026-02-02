"""
Multi-Task Workflow Parser - Intelligent task decomposition and organization
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TaskInfo:
    """Individual task information"""
    id: str
    description: str
    project_name: str
    folder_name: str
    file_suggestions: List[str]
    task_type: str  # 'website', 'script', 'document', etc.

class MultiTaskParser:
    """Parse complex multi-task descriptions into organized tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger("multi_task_parser")
    
    def parse_workflow_description(self, description: str) -> List[TaskInfo]:
        """Parse workflow description into individual tasks"""
        
        # Detect if this is a multi-task workflow
        if not self._is_multi_task(description):
            # Single task - create one task info
            return [self._create_single_task(description)]
        
        # Extract individual tasks
        tasks = self._extract_tasks(description)
        
        # Process each task
        task_infos = []
        for i, task_desc in enumerate(tasks):
            task_info = self._analyze_task(task_desc, i + 1)
            task_infos.append(task_info)
            self.logger.info(f"📋 Task {i+1}: {task_info.project_name} → {task_info.folder_name}")
        
        return task_infos
    
    def _is_multi_task(self, description: str) -> bool:
        """Detect if description contains multiple tasks"""
        multi_task_indicators = [
            r'\d+\s+tasks?',  # "2 tasks", "3 task"
            r'first.*second',  # "first ... second"
            r'then.*create',   # "then create"
            r'and.*create',    # "and create"
            r'also.*create',   # "also create"
            r'next.*task',     # "next task"
        ]
        
        desc_lower = description.lower()
        return any(re.search(pattern, desc_lower) for pattern in multi_task_indicators)
    
    def _extract_tasks(self, description: str) -> List[str]:
        """Extract individual task descriptions"""
        
        # Pattern 1: Numbered tasks (first, second, third)
        ordinal_pattern = r'(first|second|third|fourth|fifth)\s+(?:one\s+is\s+to\s+|task\s+is\s+to\s+|is\s+to\s+)?(.*?)(?=\s+(?:and\s+)?(?:second|third|fourth|fifth)|$)'
        ordinal_matches = re.findall(ordinal_pattern, description, re.IGNORECASE | re.DOTALL)
        
        if ordinal_matches:
            tasks = []
            for match in ordinal_matches:
                task_desc = match[1].strip()
                # Clean up the task description
                task_desc = re.sub(r'^\s*(?:one\s+)?is\s+to\s+', '', task_desc, flags=re.IGNORECASE)
                tasks.append(task_desc)
            return tasks
        
        # Pattern 2: "and" separated tasks with create/build keywords
        and_pattern = r'(?:create|build|make|generate|develop|design)\s+.*?(?=\s+and\s+(?:create|build|make|generate|develop|design)|\s*$)'
        and_matches = re.findall(and_pattern, description, re.IGNORECASE | re.DOTALL)
        
        if len(and_matches) > 1:
            return [match.strip() for match in and_matches]
        
        # Pattern 3: Split on task separators
        separators = [
            r'\.\s+(?:and\s+)?(?:second|third|fourth|fifth)',
            r'\.\s+(?:and\s+)?(?:then|next|also)',
            r'(?:and\s+)?(?:second|third|fourth|fifth)\s+(?:one\s+)?(?:is\s+to\s+)?'
        ]
        
        for separator in separators:
            parts = re.split(separator, description, flags=re.IGNORECASE)
            if len(parts) > 1:
                tasks = []
                for part in parts:
                    part = part.strip()
                    if part and any(keyword in part.lower() for keyword in ['create', 'build', 'make', 'generate']):
                        tasks.append(part)
                if len(tasks) > 1:
                    return tasks
        
        return [description]
    
    def _analyze_task(self, task_description: str, task_number: int) -> TaskInfo:
        """Analyze individual task and extract project information"""
        
        task_id = f"task_{task_number:02d}"
        
        # Detect project type and context
        project_info = self._extract_project_info(task_description)
        
        # Generate folder name
        folder_name = self._generate_folder_name(project_info['domain'], project_info['type'])
        
        # Suggest file names
        file_suggestions = self._suggest_filenames(project_info)
        
        return TaskInfo(
            id=task_id,
            description=task_description.strip(),
            project_name=project_info['name'],
            folder_name=folder_name,
            file_suggestions=file_suggestions,
            task_type=project_info['type']
        )
    
    def _extract_project_info(self, description: str) -> Dict[str, str]:
        """Extract project information from task description"""
        
        desc_lower = description.lower()
        
        # Domain detection
        domain_patterns = {
            'digital_agency': ['digital agency', 'marketing agency', 'creative agency', 'design agency'],
            'restaurant': ['restaurant', 'cafe', 'bistro', 'diner', 'food', 'dining'],
            'ecommerce': ['ecommerce', 'e-commerce', 'online store', 'shop', 'marketplace'],
            'portfolio': ['portfolio', 'personal website', 'resume', 'cv'],
            'blog': ['blog', 'news', 'article', 'content'],
            'corporate': ['corporate', 'business', 'company', 'enterprise'],
            'healthcare': ['healthcare', 'medical', 'clinic', 'hospital', 'health'],
            'education': ['education', 'school', 'university', 'learning', 'course'],
            'real_estate': ['real estate', 'property', 'housing', 'apartment'],
            'fitness': ['fitness', 'gym', 'workout', 'health club', 'sports']
        }
        
        detected_domain = 'general'
        for domain, keywords in domain_patterns.items():
            if any(keyword in desc_lower for keyword in keywords):
                detected_domain = domain
                break
        
        # Type detection
        if any(word in desc_lower for word in ['website', 'landing page', 'homepage', 'web']):
            project_type = 'website'
        elif any(word in desc_lower for word in ['script', 'python', 'code']):
            project_type = 'script'
        elif any(word in desc_lower for word in ['app', 'application']):
            project_type = 'application'
        else:
            project_type = 'website'  # Default
        
        # Generate project name
        project_name = detected_domain.replace('_', ' ').title()
        
        return {
            'domain': detected_domain,
            'type': project_type,
            'name': project_name
        }
    
    def _generate_folder_name(self, domain: str, project_type: str) -> str:
        """Generate intelligent folder name"""
        
        if project_type == 'website':
            return f"{domain}_website"
        elif project_type == 'script':
            return f"{domain}_scripts"
        elif project_type == 'application':
            return f"{domain}_app"
        else:
            return domain
    
    def _suggest_filenames(self, project_info: Dict[str, str]) -> List[str]:
        """Suggest appropriate filenames for the project"""
        
        domain = project_info['domain']
        project_type = project_info['type']
        
        if project_type == 'website':
            return [
                'index.html',
                'styles/main.css',
                'js/script.js',
                'assets/images/'
            ]
        elif project_type == 'script':
            return [
                f'{domain}_main.py',
                f'{domain}_utils.py',
                'config.json'
            ]
        else:
            return ['main.html', 'style.css', 'script.js']
    
    def _create_single_task(self, description: str) -> TaskInfo:
        """Create task info for single task"""
        project_info = self._extract_project_info(description)
        folder_name = self._generate_folder_name(project_info['domain'], project_info['type'])
        file_suggestions = self._suggest_filenames(project_info)
        
        return TaskInfo(
            id="task_01",
            description=description,
            project_name=project_info['name'],
            folder_name=folder_name,
            file_suggestions=file_suggestions,
            task_type=project_info['type']
        )

# Global parser instance
multi_task_parser = MultiTaskParser()
