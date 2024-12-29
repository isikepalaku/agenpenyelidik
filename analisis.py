import json
from phi.model.openai import OpenAIChat
from phi.agent import Agent, RunResponse
from phi.tools.googlesearch import GoogleSearch
from phi.workflow import Workflow
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.playground import Playground, serve_playground_app

# Initialize session storage
session_storage = SqlWorkflowStorage(
    table_name="legal_analysis_workflows",
    db_file="tmp/workflows.db"
)

# Create Research Agent for case classification
case_classification_agent = Agent(
    name="Case Classification Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="You are a legal research assistant specializing in case analysis.",
    instructions=[
        "Analyze the provided case information and classify elements into categories:",
        "1. Witnesses: People who can provide testimony about the case",
        "2. Objects: Physical items relevant to the case",
        "3. Clues: Pieces of evidence that help solve the case",
        "4. Other evidence: Any additional relevant information",
        "Return a structured list of classified elements in markdown format."
    ],
    markdown=True,
    show_tool_calls=True
)

# Create Criminal Analysis Agent
criminal_analysis_agent = Agent(
    name="Criminal Analysis Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="You are a criminal analysis expert specializing in identifying criminal acts and modus operandi.",
    instructions=[
        "Analyze the provided case facts to determine:",
        "1. The criminal act committed",
        "2. The modus operandi (method of operation)",
        "Provide a structured summary in markdown format with:",
        "- Criminal Act: [description]",
        "- Modus Operandi: [description]",
        "Be thorough and precise in your analysis."
    ],
    markdown=True,
    show_tool_calls=True
)

# Create Web Search Agent for Legal Research
web_search_agent = Agent(
    name="Legal Web Search Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[GoogleSearch()],
    description="You are a legal research assistant specializing in finding relevant articles and laws.",
    instructions=[
        "Given a legal topic or query by the user, perform a web search using Google",
        "Focus on finding relevant legal articles, case law, and legislation",
        "Return the top 5 most authoritative and relevant results",
        "For each result, include:",
        "- Title of the article/law",
        "- Source (website or publication)",
        "- URL",
        "- Brief summary of the content",
        "- Date of publication (if available)",
        "Always verify the credibility of sources, prioritizing government and academic sources",
        "Format the results in markdown for easy reading",
        "Document all sources properly for legal citation"
    ],
    markdown=True,
    show_tool_calls=True
)

# Create multi-agent team with session state
agent_team = Workflow(
    name="Legal Analysis Workflow",
    team=[case_classification_agent, criminal_analysis_agent, web_search_agent],
    markdown=True,
    show_tool_calls=True,
    storage=session_storage,
    stream=True  # Enable streaming
)

def get_session_state(session_id: str):
    """Retrieve session state for a given session ID"""
    return session_storage.read(session_id)

def save_session_state(session_id: str, data: dict):
    """Save data to session state"""
    session_storage.upsert(session_id, data)

def classify_case_elements(case_info: str, session_id: str = "default") -> str:
    """Classify case elements using the research agent with caching"""
    agent_team.session_id = session_id
    
    # Check cache
    if "case_classification" in agent_team.session_state:
        cached_result = next((r for r in agent_team.session_state["case_classification"] if r["case_info"] == case_info), None)
        if cached_result:
            return cached_result["classification"]
    
    # Perform classification
    response: RunResponse = case_classification_agent.run(
        f"Classify the following case elements:\n{case_info}"
    )
    
    # Cache result
    if "case_classification" not in agent_team.session_state:
        agent_team.session_state["case_classification"] = []
    agent_team.session_state["case_classification"].append({
        "case_info": case_info,
        "classification": response.content
    })
    agent_team.write_to_storage()
    
    return response.content

def analyze_criminal_acts(case_facts: str, session_id: str = "default") -> str:
    """Analyze criminal case facts and identify act + modus operandi with caching"""
    agent_team.session_id = session_id
    
    # Check cache
    if "criminal_analysis" in agent_team.session_state:
        cached_result = next((r for r in agent_team.session_state["criminal_analysis"] if r["case_facts"] == case_facts), None)
        if cached_result:
            return cached_result["analysis"]
    
    # Perform analysis
    response: RunResponse = criminal_analysis_agent.run(
        f"Analyze the following case facts:\n{case_facts}"
    )
    
    # Cache result
    if "criminal_analysis" not in agent_team.session_state:
        agent_team.session_state["criminal_analysis"] = []
    agent_team.session_state["criminal_analysis"].append({
        "case_facts": case_facts,
        "analysis": response.content
    })
    agent_team.write_to_storage()
    
    return response.content

def search_legal_articles(query: str, session_id: str = "default") -> str:
    """Search for legal articles and laws using the web search agent with caching"""
    agent_team.session_id = session_id
    
    # Check cache
    if "legal_search" in agent_team.session_state:
        cached_result = next((r for r in agent_team.session_state["legal_search"] if r["query"] == query), None)
        if cached_result:
            return cached_result["results"]
    
    # Perform search
    response: RunResponse = web_search_agent.run(
        f"Search for legal articles and laws related to: {query}"
    )
    
    # Cache result
    if "legal_search" not in agent_team.session_state:
        agent_team.session_state["legal_search"] = []
    agent_team.session_state["legal_search"].append({
        "query": query,
        "results": response.content
    })
    agent_team.write_to_storage()
    
    return response.content

# Create Report Writer Agent
report_writer_agent = Agent(
    name="Report Writer Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="You are a legal report writer specializing in creating comprehensive legal analysis reports.",
    instructions=[
        "You will be provided with case analysis data including:",
        "- Case element classifications",
        "- Criminal act and modus operandi analysis",
        "- Relevant legal articles and laws",
        "Generate a comprehensive legal analysis report in the following format:",
        "## Case Overview",
        "### Case Elements",
        "{classification results}",
        "### Criminal Analysis",
        "{criminal act and modus operandi}",
        "### Legal References",
        "{relevant articles and laws}",
        "### Summary and Recommendations",
        "{summary and recommendations based on the analysis}",
        "Ensure the report is well-structured, professional, and includes all relevant details.",
        "Use proper legal terminology and maintain a formal tone throughout."
    ],
    markdown=True,
    show_tool_calls=True
)

# Create Playground UI
app = Playground(
    agents=[
        case_classification_agent,
        criminal_analysis_agent,
        web_search_agent,
        report_writer_agent
    ]
).get_app()

if __name__ == "__main__":
    serve_playground_app("analisis:app", reload=True)

def generate_legal_report(case_info: str, session_id: str = "default") -> str:
    """Generate a comprehensive legal analysis report"""
    agent_team.session_id = session_id
    
    # Check cache
    if "legal_reports" in agent_team.session_state:
        cached_result = next((r for r in agent_team.session_state["legal_reports"] if r["case_info"] == case_info), None)
        if cached_result:
            return cached_result["report"]
    
    # Gather all analysis data
    classification = classify_case_elements(case_info, session_id)
    criminal_analysis = analyze_criminal_acts(case_info, session_id)
    legal_articles = search_legal_articles(case_info, session_id)
    
    # Prepare report input
    report_input = {
        "case_info": case_info,
        "classification": classification,
        "criminal_analysis": criminal_analysis,
        "legal_articles": legal_articles
    }
    
    # Generate report
    response: RunResponse = report_writer_agent.run(
        f"Generate a legal analysis report based on the following data:\n{json.dumps(report_input, indent=2)}"
    )
    
    # Cache result
    if "legal_reports" not in agent_team.session_state:
        agent_team.session_state["legal_reports"] = []
    agent_team.session_state["legal_reports"].append({
        "case_info": case_info,
        "report": response.content
    })
    agent_team.write_to_storage()
    
    return response.content
