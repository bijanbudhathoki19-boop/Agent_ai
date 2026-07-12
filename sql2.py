import os
import re
import logging
import asyncio
import pandas as pd
import numpy as np
from crewai import Agent, Task, Crew, Process, LLM
from e2b_code_interpreter import AsyncSandbox

# ==========================================================================================
# 1. ROBUST LOGGER CONFIGURATION (Targets data_analysis.logs exclusively)
# ==========================================================================================
logger = logging.getLogger("MiningCrew")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

# Establish a strict local file logging transaction stream
file_handler = logging.FileHandler("data_analysis.logs", mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

# Capture internal framework diagnostic metrics out of crewai and pipe them into the log asset
crewai_logger = logging.getLogger("crewai")
crewai_logger.setLevel(logging.INFO)
crewai_logger.addHandler(file_handler)

# ==========================================================================================
# 2. PRODUCTION CREDENTIAL CONTEXT CONFIGURATION
# ==========================================================================================
os.environ["OPENAI_API_KEY"] = "your key"
os.environ["E2B_API_KEY"] = "your key"

llm = LLM(model="gpt-4o", temperature=0.1) #use your model 

# ==========================================================================================
# 3. SYNTHETIC CORPORATE RESOURCE GENERATION
# ==========================================================================================
def generate_local_csv():
    logger.info("Initializing synthetic mining operational dataset...")
    try:
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=25, freq='D')
        data = {
            'Date': dates,
            'Mine_ID': np.random.choice(['Mine_A', 'Mine_B', 'Mine_C', 'Mine_D'], 25),
            'Ore_Tons': np.random.randint(1200, 4500, 25),
            'Gold_g_per_ton': np.round(np.random.uniform(1.5, 7.8, 25), 2),
            'Silver_g_per_ton': np.round(np.random.uniform(20, 90, 25), 1),
            'Efficiency_%': np.round(np.random.uniform(75, 95, 25), 1),
            'Cost_USD': np.random.randint(52000, 165000, 25),
            'Revenue_USD': np.random.randint(180000, 720000, 25),
            'Incidents': np.random.randint(0, 4, 25),
        }
        df = pd.DataFrame(data)
        df['Profit_USD'] = df['Revenue_USD'] - df['Cost_USD']
        df['Profit_Margin'] = round((df['Profit_USD'] / df['Revenue_USD']) * 100, 2)
        csv_path = "mining_data.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Locally staged dataset saved under filepath: '{csv_path}'")
        return csv_path
    except Exception as e:
        logger.error(f"❌ Critical Failure while creating source mining_data.csv file context: {str(e)}")
        raise

# ==========================================================================================
# 4. CONCURRENT INTERACTIVE SANDBOX PROCESSING CONTAINER (NON-BLOCKING)
# ==========================================================================================
async def execute_in_sandbox_async(python_code: str) -> str:
    logger.info("🔧 Bootstrapping remote E2B cloud microVM context (Async)...")
    
    try:
        # Spin up execution instance concurrently to eliminate thread execution locks
        sandbox = await AsyncSandbox.create()
    except Exception as startup_err:
        fallback_msg = f"CRITICAL FALLBACK: E2B Sandbox instantiation rejected by network gateway: {str(startup_err)}"
        logger.error(fallback_msg)
        return fallback_msg

    try:
        csv_file_path = "mining_data.csv"
        if os.path.exists(csv_file_path):
            with open(csv_file_path, "rb") as f:
                await sandbox.files.write("/data.csv", f)
            logger.info("📦 Successfully mounted dataset payload to remote VM path target '/data.csv'")
        else:
            raise FileNotFoundError("Missing local 'mining_data.csv' source asset dependencies.")

        # Extricate any markdown block notation formatting artifacts safely
        clean_code = python_code
        if "```python" in clean_code:
            clean_code = clean_code.split("```python")[1].split("```")[0].strip()
        elif "```" in clean_code:
            clean_code = clean_code.split("```")[1].split("```")[0].strip()

        logger.info("🚀 Passing code payload down to execution sandbox interpreter frame...")
        execution = await sandbox.run_code(clean_code)

        if execution.error:
            error_details = f"Sandbox Processing Error Intercepted:\nName: {execution.error.name}\nValue: {execution.error.value}\nTraceback: {execution.error.traceback}"
            logger.error(f"❌ {error_details}")
            return f"Runtime Error Occurred Inside Isolation Container:\n{execution.error.value}"

        logs_output = execution.logs.stdout
        combined_logs = "\n".join(logs_output) if isinstance(logs_output, list) else str(logs_output)
        
        logger.info("📥 Captured code calculation data logs via sandbox stdout streams.")
        return combined_logs if combined_logs.strip() else "Code executed cleanly, but returned empty stdout stream."
    
    except Exception as exc:
        fallback_exception_msg = f"FALLBACK WARNING: Local transaction processing manager crashed during environment coordination: {str(exc)}"
        logger.exception(fallback_exception_msg)
        return fallback_exception_msg
    finally:
        logger.info("🔌 Shutting down cloud microVM workspace securely.")
        await sandbox.kill()

# ==========================================================================================
# 5. CREWAI AGENTS SYSTEM ARTIFACT ARCHITECTURES
# ==========================================================================================
logger.info("Building CrewAI orchestration definitions...")

code_generator_agent = Agent(
    role="Senior Core Python Data Scientist",
    goal="Write precise Python script assets using pandas to run deep aggregation analytics on a structured data source.",
    backstory="You are an expert computational architect specializing in structured data environments. You write pure, self-contained Python code blocks designed to aggregate files and log exact metrics.",
    llm=llm,
    allow_delegation=False,
    verbose=False
)

report_writer_agent = Agent(
    role="Lead Mining Industry Business Intelligence Analyst",
    goal="Convert raw technical output and calculations into high-end executive markdown documents.",
    backstory="You are a principal sector strategist. You translate execution statistics directly into clear analytics layouts with clean markdown data blocks.",
    llm=llm,
    allow_delegation=False,
    verbose=False
)

# ==========================================================================================
# 6. ASYNCHRONOUS COMPILATION EXECUTION ENGINE
# ==========================================================================================
async def run_analysis_pipeline():
    logger.info("🎬 Beginning multi-agent computational transaction sequence...")
    
    # Pre-flight resource tracking initialization
    generate_local_csv()
    
    user_query = "Perform full EDA with insights and find out which mine is most profitable with full metric comparisons."
    logger.info(f"📥 Loaded Target Analysis Query: '{user_query}'")

    # Task 1 Configuration Block
    code_generation_task = Task(
        description=(
            f"Write a complete Python code block targeting a CSV dataset located at path '/data.csv'.\n\n"
            f"The dataset contains the exact following schema properties:\n"
            f"- Columns: ['Date', 'Mine_ID', 'Ore_Tons', 'Gold_g_per_ton', 'Silver_g_per_ton', 'Efficiency_%', 'Cost_USD', 'Revenue_USD', 'Incidents', 'Profit_USD', 'Profit_Margin']\n\n"
            f"The script must perform data analysis explicitly answering this User Request: '{user_query}'\n"
            f"Make sure to group performance calculations by the 'Mine_ID' column and aggregate operational metrics (Profit_USD, Profit_Margin, Incidents).\n\n"
            "CRITICAL REQUIREMENT: The code must include explicit print() statements to log all aggregated DataFrames "
            "and statistics directly to the terminal stdout stream so they are caught by the logging runtime.\n"
            "Return ONLY the executable Python script string inside a python markdown wrapper block. Do not append conversational descriptions."
        ),
        expected_output="A pure, clean executable Python string containing pandas scripts designed to output raw statistics.",
        agent=code_generator_agent
    )

    crew = Crew(
        agents=[code_generator_agent],
        tasks=[code_generation_task],
        process=Process.sequential,
        verbose=False
    )
    
    logger.info("🚀 Executing Step 1: Querying LLM for Data Science Code Block...")
    raw_code_output = await crew.kickoff_async()
    python_script_string = getattr(raw_code_output, "raw", str(raw_code_output))
    
    # Run Step 2 (Async Cloud Compute Translation)
    logger.info("🚀 Executing Step 2: Spinning up secure E2B container sandbox...")
    sandbox_metrics_data = await execute_in_sandbox_async(python_script_string)
    
    logger.info("📥 Sandbox calculations retrieved successfully. Passing dataset results to Writer Agent configuration environment...")

    # Task 2 Configuration Block
    report_generation_task = Task(
        description=(
            f"Review the raw statistics provided from the database pipeline execution regarding the user's inquiry: '{user_query}'.\n"
            f"Data payload from execution environment:\n\n{sandbox_metrics_data}\n\n"
            "Transform those raw metrics into a comprehensive, executive-ready analytical report.\n\n"
            "The report must be written in crisp Markdown format (.md) and include:\n"
            "- A professional Title Heading\n"
            "- An Executive Summary explicitly answering the user's initial inquiry\n"
            "- Structured markdown data tables comparing all calculated values\n"
            "- A clear data-driven conclusion\n\n"
            "Do not include conversational greetings. Output only the raw markdown text."
        ),
        expected_output="A polished, executive-level production Markdown report detailing the full performance analysis.",
        agent=report_writer_agent
    )

    writing_crew = Crew(
        agents=[report_writer_agent],
        tasks=[report_generation_task],
        process=Process.sequential,
        verbose=False
    )
    
    logger.info("🚀 Executing Step 3: Compiling structured report via Corporate Reporting Agent...")
    raw_final_report = await writing_crew.kickoff_async()
    markdown_content = getattr(raw_final_report, "raw", str(raw_final_report))

    # ==========================================================================================
    # 7. EXPLICIT STORAGE WRITING ENGINE (Bypasses Framework Serialization Bugs)
    # ==========================================================================================
    output_filepath = os.path.abspath("output.md")
    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"✅ Production execution pipeline success! Compiled markdown committed to disk at: {output_filepath}")
        
        # Simple terminal notifications to let the developer know the process finished
        print("\n" + "="*80)
        print(" 🎉 PIPELINE TRANSACTION COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f" 📑 Execution Logs Saved File :  {os.path.abspath('data_analysis.logs')}")
        print(f" 📊 Report Asset Generated At  :  {output_filepath}")
        print("="*80 + "\n")
        
    except Exception as file_err:
        logger.error(f"❌ Failed writing the output document payload onto local disk block storage: {str(file_err)}")
        print(f"\n❌ Write Error: Unable to store markdown file to output.md directory. Check data_analysis.logs for details.\n")

# ==========================================================================================
# 8. MULTI-ENVIRONMENT ASYNC EXECUTION CONTAINER SAFETY HOOK
# ==========================================================================================
if __name__ == "__main__":
    try:
        # Query if an active execution loop framework already possesses system focus
        loop = asyncio.get_running_loop()
        if loop.is_running():
            logger.info("⚡ Active execution environment frame caught. Registering pipeline execution onto current thread loop...")
            task = loop.create_task(run_analysis_pipeline())
            
            # Explicit monitoring engine hook capturing dynamic task processing errors
            def handle_task_result(t):
                try:
                    t.result()
                except Exception as e:
                    logger.critical(f"Pipeline background scheduler crashed unexpectedly: {str(e)}")
                    print(f"\n❌ Loop Failure Warning: Execution crashed background routine context: {e}\n")
            task.add_done_callback(handle_task_result)
            
    except RuntimeError:
        # Pure decoupled standard terminal environment run profile execution
        logger.info("💻 Decoupled terminal execution context mapped. Starting isolated execution routine...")
        asyncio.run(run_analysis_pipeline())