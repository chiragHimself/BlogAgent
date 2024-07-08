__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3


from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Set API key environment variable
os.environ["OPENAI_API_KEY"] = "NA"
#tracing with langsmith


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Define agents
planner = Agent(
    role="Content Planner",
    goal="Plan engaging and factually accurate content on {topic}",
    backstory="You're working on planning a blog article about the topic: {topic}. "
              "You collect information that helps the audience learn something "
              "and make informed decisions. Your work is the basis for the Content Writer to write an article on this topic.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal="Write an insightful and factually accurate opinion piece about the topic: {topic}",
    backstory="You're working on writing a new opinion piece about the topic: {topic}. "
              "You base your writing on the work of the Content Planner, who provides an outline and relevant context about the topic. "
              "You follow the main objectives and direction of the outline, providing objective and impartial insights backed by information provided by the Content Planner.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

editor = Agent(
    role="Editor",
    goal="Edit a given blog post to align with the writing style of the organization and ensure the final output shall be of maximum {limit} words.",
    backstory="You are an editor who receives a blog post from the Content Writer. "
              "Your goal is to review the blog post to ensure that it follows journalistic best practices, provides balanced viewpoints, "
              "and avoids major controversial topics or opinions when possible.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Define tasks
plan = Task(
    description=(
        "1. Prioritize the latest trends, key players, and noteworthy news on {topic}.\n"
        "2. Identify the target audience, considering their interests and pain points.\n"
        "3. Develop a detailed content outline including an introduction, key points, and a call to action.\n"
        "4. Include SEO keywords and relevant data or sources."
    ),
    expected_output="A comprehensive content plan document with an outline, audience analysis, SEO keywords, and resources.",
    agent=planner,
)

write = Task(
    description=(
        "1. Use the content plan to craft a compelling blog post on {topic}.\n"
        "2. Incorporate SEO keywords naturally.\n"
        "3. Sections/Subtitles are properly named in an engaging manner.\n"
        "4. Ensure the post is structured with an engaging introduction, insightful body, and a summarizing conclusion.\n"
        "5. Proofread for grammatical errors and alignment with the brand's voice."
    ),
    expected_output="A well-written blog post in markdown format, ready for publication, each section should have 2 or 3 paragraphs.",
    agent=writer,
)

edit = Task(
    description=("Proofread the given blog post for grammatical errors and alignment with the brand's voice. Must trim down the response to {limit} words."),
    expected_output="A well-written blog post in markdown format, ready for publication, each section should have 2 or 3 paragraphs.",
    agent=editor
)

crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    verbose=2
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        color: #FFF8F3;
        font-family: 'Baskervville SC',Roboto;
        text-align: center;
    }
    .subheader {
        color: #758694;
        font-family: 'Roboto', Baskervville SC;
        text-align: center;
    }
    .input-section {
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit App
st.markdown('<h1 class="main-title">Article Dada 👑</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="subheader">Generate comprehensive articles in less than 15 seconds</h2>', unsafe_allow_html=True)

# Input section
st.markdown('<div class="input-section">', unsafe_allow_html=True)
query = st.text_input("Enter the topic:", placeholder="e.g., Artificial Intelligence")
limit = st.text_input("Enter the word limit in words:", placeholder="e.g., 500")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("###### Please note the word limit might vary by 50 words to ensure a perfect response in few cases.")

# Submit button
if st.button("Submit"):
    if query:
        try:
            with st.spinner('Article generating...  have some water meanwhile🥤'):
                response = crew.kickoff(inputs={"topic": query, "limit": limit})
                st.success("Article generated successfully!")
                st.write(response)
        except Exception as e:
            st.error("Error: Please enter a valid title and avoid controversial topics as we won't respond to that. Thanks!")
    else:
        st.warning("Please enter a topic to generate!")
