import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

class ComplianceIssue(TypedDict):
    category: str           # e.g., "FTC_DISCLOSURE"
    description: str        # Specific detail of the violation
    severity: str           # "CRITICAL" | "WARNING"
    timestamp: Optional[str]# Timestamp of occurrence (if applicable)

class VideoAuditState(TypedDict):
    """
    Defines the data schema for the LangGraph execution context.
    """
    video_url: str
    video_id: str

    local_file_path: Optional[str]  
    video_metadata: Dict[str, Any]  
    transcript: Optional[str]       
    ocr_text: List[str]            

    compliance_results: Annotated[List[ComplianceIssue], operator.add] 
    final_status: str            
    final_report: str               
    
    errors: Annotated[List[str], operator.add]