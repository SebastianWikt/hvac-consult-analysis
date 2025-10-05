import json
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict


class CallData:
    """
    Class to process and structure call transcript data from JSON files.
    Handles parsing of call metadata, compliance checks, and utterances.
    """
    
    def __init__(self, json_data: Dict[str, Any]):
        """
        Initialize CallData with JSON data.
        
        Args:
            json_data: Dictionary containing call data from JSON file
        """
        self.meta = json_data.get('meta', {})
        self.compliance_check = json_data.get('compliance_check', [])
        self.utterances = json_data.get('utterances', [])
        self.segments = json_data.get('segments', [])
        self.sales_insights = json_data.get('sales_insights', [])
        self.full_transcript = json_data.get('full_transcript', '')
        
    def get_stages(self) -> List[str]:
        """
        Extract unique stages from compliance check data.
        
        Returns:
            List of stage names in order
        """
        stages = []
        for check in self.compliance_check:
            stage = check.get('stage')
            if stage and stage not in stages:
                stages.append(stage)
        return stages
    
    def get_utterances_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """
        Get all utterances for a specific stage.
        
        Args:
            stage: Stage name to filter by
            
        Returns:
            List of utterances for the specified stage
        """
        return [
            utterance for utterance in self.utterances 
            if utterance.get('stage') == stage
        ]
    
    def get_all_utterances_grouped_by_stage(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group all utterances by their stage.
        
        Returns:
            Dictionary with stage names as keys and lists of utterances as values
        """
        grouped = defaultdict(list)
        for utterance in self.utterances:
            stage = utterance.get('stage', 'General')
            grouped[stage].append(utterance)
        return dict(grouped)
    
    def get_compliance_data(self, stage: str) -> Optional[Dict[str, Any]]:
        """
        Get compliance data for a specific stage.
        
        Args:
            stage: Stage name to get compliance data for
            
        Returns:
            Dictionary containing score, evidence, and suggestions for the stage
        """
        for check in self.compliance_check:
            if check.get('stage') == stage:
                return {
                    'score': check.get('score', 0),
                    'max_score': check.get('max', 5),
                    'evidence': check.get('evidence', ''),
                    'suggestion': check.get('suggestion', '')
                }
        return None
    
    def get_all_compliance_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all compliance data organized by stage.
        
        Returns:
            Dictionary with stage names as keys and compliance data as values
        """
        compliance_data = {}
        for check in self.compliance_check:
            stage = check.get('stage')
            if stage:
                compliance_data[stage] = {
                    'score': check.get('score', 0),
                    'max_score': check.get('max', 5),
                    'evidence': check.get('evidence', ''),
                    'suggestion': check.get('suggestion', '')
                }
        return compliance_data
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp from seconds to MM:SS format.
        
        Args:
            seconds: Timestamp in seconds
            
        Returns:
            Formatted timestamp string
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_call_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the call data.
        
        Returns:
            Dictionary containing call summary information
        """
        total_utterances = len(self.utterances)
        stages = self.get_stages()
        total_compliance_score = sum(
            check.get('score', 0) for check in self.compliance_check
        )
        max_compliance_score = sum(
            check.get('max', 5) for check in self.compliance_check
        )
        
        return {
            'call_type': self.meta.get('call_type', 'Unknown'),
            'date_analyzed': self.meta.get('date_analyzed', 'Unknown'),
            'total_utterances': total_utterances,
            'total_stages': len(stages),
            'stages': stages,
            'compliance_score': total_compliance_score,
            'max_compliance_score': max_compliance_score,
            'compliance_percentage': (
                (total_compliance_score / max_compliance_score * 100) 
                if max_compliance_score > 0 else 0
            )
        }

    @classmethod
    def from_json_file(cls, file_path: str) -> 'CallData':
        """
        Create CallData instance from JSON file.
        
        Args:
            file_path: Path to JSON file containing call data
            
        Returns:
            CallData instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Call data file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            return cls(json_data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e}")


class CustomAnalysis:
    """
    Class to handle custom analysis data from static files.
    Allows for easy editing of analysis content without database changes.
    """
    
    def __init__(self, analysis_file_path: str):
        """
        Initialize CustomAnalysis with file path.
        
        Args:
            analysis_file_path: Path to JSON file containing custom analysis
        """
        self.analysis_file_path = analysis_file_path
        self.analysis_data = self.load_analysis_file()
    
    def load_analysis_file(self) -> Dict[str, Any]:
        """
        Load custom analysis data from file.
        
        Returns:
            Dictionary containing custom analysis data
        """
        if not os.path.exists(self.analysis_file_path):
            # Return empty structure if file doesn't exist
            return {'stages': {}}
        
        try:
            with open(self.analysis_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # Return empty structure if file is invalid
            return {'stages': {}}
    
    def get_stage_analysis(self, stage: str) -> Dict[str, Any]:
        """
        Get custom analysis for a specific stage.
        
        Args:
            stage: Stage name to get analysis for
            
        Returns:
            Dictionary containing custom analysis for the stage
        """
        stages_data = self.analysis_data.get('stages', {})
        return stages_data.get(stage, {
            'analysis': '',
            'key_points': [],
            'recommendations': []
        })
    
    def get_all_stage_analysis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all custom analysis data organized by stage.
        
        Returns:
            Dictionary with stage names as keys and analysis data as values
        """
        return self.analysis_data.get('stages', {})
    
    def has_analysis_for_stage(self, stage: str) -> bool:
        """
        Check if custom analysis exists for a specific stage.
        
        Args:
            stage: Stage name to check
            
        Returns:
            True if analysis exists for the stage, False otherwise
        """
        stages_data = self.analysis_data.get('stages', {})
        stage_data = stages_data.get(stage, {})
        return bool(
            stage_data.get('analysis') or 
            stage_data.get('key_points') or 
            stage_data.get('recommendations')
        )