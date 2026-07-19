import uuid       
import logging   
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel  
from typing import List, Optional  

from dotenv import load_dotenv
load_dotenv(override=True)  

from backend.src.api.telemetry import setup_telemetry
setup_telemetry()  

from backend.src.graph.workflow import app as compliance_graph

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger("api-server")  


app = FastAPI(
    title="Brand Guardian AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"
)

class AuditRequest(BaseModel):
    video_url: str  



class ComplianceIssue(BaseModel):
    """
    Defines the structure of a single compliance violation.
    
    Used inside AuditResponse to represent each violation found.
    """
    category: str    
    severity: str     
    description: str   

class AuditResponse(BaseModel):
    session_id: str                         
    video_id: str                            
    status: str                          
    final_report: str                    
    compliance_results: List[ComplianceIssue] 
    errors: List[str] = [] 


@app.post("/audit", response_model=AuditResponse)
async def audit_video(request: AuditRequest):
    """
    Main API endpoint that triggers the compliance audit workflow.
    """
    session_id = str(uuid.uuid4())  
    
    video_id_short = f"vid_{session_id[:8]}"  
    logger.info(f"Received Audit Request: {request.video_url} (Session: {session_id})")
    initial_inputs = {
        "video_url": request.video_url,  
        "video_id": video_id_short,     
        "compliance_results": [],        
        "errors": []                  
    }

    try:
        final_state = compliance_graph.invoke(initial_inputs)
        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),  
            status=final_state.get("final_status", "UNKNOWN"),  
            final_report=final_state.get("final_report", "No report generated."),
            compliance_results=final_state.get("compliance_results", []),
            errors=final_state.get("errors", [])
        )
    
    except Exception as e:
        logger.error(f"Audit Failed: {str(e)}")  
        raise HTTPException(
            status_code=500,  
            detail=f"Workflow Execution Failed: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Brand Guardian AI"}