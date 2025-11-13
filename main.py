from crewai import Crew, Agent, Task, Process, LLM
from crewai.tools import BaseTool
from dotenv import load_dotenv
import pandas as pd
from os import getenv
from pydantic import BaseModel, Field
from crewai_tools import CodeInterpreterTool
from src.models import JupyterNotebook, MarkdownCell, CodeCell


load_dotenv()

llm = LLM(
    model="openrouter/google/gemini-2.5-pro",
    base_url="https://openrouter.ai/api/v1",
    api_key=getenv("OPENROUTER_API_KEY")
)


company_name = "Gucci"
dataset_description = "second luxury selling" 
dataset_path = "example_data/vestiaire.csv"

df =  pd.read_csv(dataset_path)
columns = ", ".join(df.columns.tolist())


code_interpreter_tool = CodeInterpreterTool()
tools = [code_interpreter_tool]

    
# Analyze Planer Agent
analyze_planer_agent = Agent(
    role="Data Analyst Expert",
    goal="Perform comprehensive data analysis processes steps including data cleaning,Exploratory Data Analysis (EDA), insights and predictions",
    backstory="""
    You are a senior data analyst with expertise in statistical analysis, data quality assessment,
    and creating meaningful visualizations get ready for insightful presentation for stakeholder. You excel at extracting insights from complex datasets and identifying patterns, trends, and anomalies.
    
    Your approach:
    1. Thoroughly understand the data structure and quality
    2. clean the data to ensure accuracy
    3. Feature engineering and statistical analysis to uncover insights
    4. Create visualizations to effectively communicate findings
    5. Provide actionable recommendations based on the analysis
    6. Suggest predictive models and strategies to enhance business outcomes
    """,
    tools=tools,
    llm=llm,
    verbose=True
)

# Analyze Coder Agent
analyze_coder_agent = Agent(
    role="Expert Python Developer",
    goal="Write clean, efficient Python code based on a given data analysis plan. Your output will copy the markdown requests you get save it as a MarkdownCell, then follow by the python code you write save it as a CodeCell, assemble both into a Jupyter Notebook JSON object. Your output must *only* be the final Jupyter Notebook JSON object, with no explanations, markdown, or 'python' tags.",
    backstory="You are a senior Python developer who writes production-ready code. You never add any conversational text to your code output.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


# Define the analysis task
analyze_planer_task = Task(
    description=f"""
    Analyze {dataset_description} dataset for company {company_name}, dedicate to give selling strategy suggestion for {company_name} stakeholder, here's the dataset's path {dataset_path}, and the columns '{columns}'. Give me a step by step process to analyze this data to give a presentation to the stakeholder, show the a insightful summary and selling strategy suggestion.
    
    CRITICAL: You will only give the data analysis process plan in markdown format, do NOT write any code at this session. Save the processed data after cleaning as 'cleaned_data.csv' for the next steps. Write detailed steps for each part, the next data analysis will write code based on this plan.

    Your analysis plan must include:
    - Data loading and cleaning steps to ensure accuracy
    - Exploratory Data Analysis (EDA) to uncover insights
    - Insights and predictions based on the analysis
    - Actionable recommendations for business strategies
    - Predictive models suggestions to enhance business outcomes
       
    """,
    expected_output="""
    Complete data analysis process planing including:
    - Data loading and cleaning steps to ensure accuracy
    - Exploratory Data Analysis (EDA) to uncover insights
    - Insights and predictions based on the analysis
    - Actionable recommendations for business strategies
    - Predictive models suggestions to enhance business outcomes
    """,
    output_file="analysis_plan.md",
    agent=analyze_planer_agent
)


analyze_coder_task = Task(
    description=f"""Write the Python code for a script that will follow the data analysis plan provided in 'analysis_plan.md'. Only use python libs including pandas,openpyxl,numpy,matplotlib,seaborn,plotly,scikit-learn. Assemble the explanation and code into a Jupyter Notebook file. The markdown cell must come first, followed by the code cell. Ensure all code lines are individual strings in the 'source' list, ending with '\\n'.
    
    Your output will following this rules: 
    - You will write python after each step in the plan, the plan part will save as a MarkdownCell, and code will be save as a CodeCell. The expected output will be MarkdownCell, CodeCell, MarkdownCell, CodeCell,....
    - For every small step that expecting to plot a figure, you must write the code to plot the figure right after the markdown explanation of that step. Make sure every CodeCell can only plotted a figure.
    - Refer to use plotly for visualization, use to_image() with scale=3 to export image data, then use IPython.display -> Image to show the figure. Only use matplotlib when plotly is not available.
    """,
    expected_output="A final Jupyter Notebook JSON object that includes the markdown explanation and the corresponding Python code which perfectly matches the JupyterNotebook Pydantic model.",
    context=[analyze_planer_task],  # Gets output from the first task
    output_pydantic=JupyterNotebook,
    output_file="analysis_report.ipynb",
    agent=analyze_coder_agent
)

crew = Crew(
    agents=[analyze_planer_agent, analyze_coder_agent],
    tasks=[analyze_planer_task, analyze_coder_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    result = crew.kickoff()
    print(result)
