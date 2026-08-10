
from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import streamlit as st

from google import genai


# =========================================================
# GEMINI API SETUP
# =========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing from your .env file.")
    st.stop()

client = genai.Client(
    api_key=GOOGLE_API_KEY
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Text to SQL App",
    page_icon="🗄️",
    layout="wide"
)


# =========================================================
# GEMINI RESPONSE FUNCTION
# =========================================================

def get_gemini_response(question, prompt):

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt + "\n\nQuestion: " + question
    )

    return response.text


# =========================================================
# SQL QUERY FUNCTION
# =========================================================

def read_sql_query(sql, database):

    try:

        connection = sqlite3.connect(database)

        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        connection.close()

        return rows

    except Exception as e:

        return f"SQL Error: {e}"


# =========================================================
# SQL PROMPT
# =========================================================

prompt = """
You are an expert in converting English questions into SQL queries.

The SQLite database contains a table named STUDENT.

The STUDENT table has these columns:

NAME
CLASS
SECTION
MARKS

Examples:

Example 1:

Question:
How many students are there?

SQL:
SELECT COUNT(*) FROM STUDENT;


Example 2:

Question:
Show all students from 10th class.

SQL:
SELECT * FROM STUDENT
WHERE CLASS = '10th';


Example 3:

Question:
Who has the highest marks?

SQL:
SELECT * FROM STUDENT
ORDER BY MARKS DESC
LIMIT 1;


Example 4:

Question:
Show students who scored more than 80 marks.

SQL:
SELECT * FROM STUDENT
WHERE MARKS > 80;


IMPORTANT RULES:

1. Return ONLY the SQL query.
2. Do not include ``` at the beginning.
3. Do not include ``` at the end.
4. Do not write the word SQL.
5. Use only the STUDENT table.
6. Use only these columns:
   NAME, CLASS, SECTION, MARKS
7. Only generate SELECT queries.
8. Never generate INSERT.
9. Never generate UPDATE.
10. Never generate DELETE.
11. Never generate DROP.
12. Never generate CREATE.
13. Never generate ALTER.
14. Never generate TRUNCATE.
"""


# =========================================================
# STREAMLIT UI
# =========================================================

st.title("🗄️ Text to SQL App")

st.write(
    "Ask questions about your Student database using normal English."
)

st.divider()


# =========================================================
# DATABASE
# =========================================================

DATABASE = "student.db"


if not os.path.exists(DATABASE):

    st.error(
        "❌ student.db was not found."
    )

    st.info(
        "Make sure student.db is in the same folder as this Python file."
    )

    st.stop()


st.success(
    "🟢 Connected to student.db"
)


# =========================================================
# SHOW DATABASE TABLE
# =========================================================

with st.expander("📋 View Student Records"):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM STUDENT"
        )

        records = cursor.fetchall()

        connection.close()


        if records:

            st.dataframe(
                records,
                use_container_width=True
            )

        else:

            st.info(
                "No records found in STUDENT table."
            )

    except Exception as e:

        st.error(
            f"Database error: {e}"
        )


# =========================================================
# USER QUESTION
# =========================================================

st.subheader("💬 Ask Your Question")

question = st.text_input(
    "Enter your question:",
    placeholder="Example: Who got the highest marks?"
)


# =========================================================
# ASK BUTTON
# =========================================================

if st.button(
    "🔍 Ask Question",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # =====================================================
    # GENERATE SQL
    # =====================================================

    with st.spinner(
        "🤖 Gemini is generating SQL..."
    ):

        try:

            sql_query = get_gemini_response(
                question,
                prompt
            )

        except Exception as e:

            st.error(
                "❌ Gemini API Error"
            )

            st.exception(e)

            st.stop()


    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    sql_query = sql_query.strip()

    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```SQL",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    sql_query = sql_query.strip()


    # =====================================================
    # DISPLAY GENERATED SQL
    # =====================================================

    st.subheader("📝 Generated SQL")

    st.code(
        sql_query,
        language="sql"
    )


    # =====================================================
    # SECURITY CHECK
    # =====================================================

    sql_upper = sql_query.upper().strip()


    # Only SELECT queries allowed

    if not sql_upper.startswith("SELECT"):

        st.error(
            "❌ Only SELECT queries are allowed."
        )

        st.stop()


    # Dangerous commands

    forbidden_commands = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "TRUNCATE"
    ]


    for command in forbidden_commands:

        if command in sql_upper:

            st.error(
                f"❌ Unsafe SQL command detected: {command}"
            )

            st.stop()


    # =====================================================
    # EXECUTE QUERY
    # =====================================================

    with st.spinner(
        "🔎 Searching database..."
    ):

        result = read_sql_query(
            sql_query,
            DATABASE
        )


    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    st.subheader("📊 Result")


    if isinstance(result, str):

        st.error(result)


    elif result:

        st.dataframe(
            result,
            use_container_width=True
        )


    else:

        st.info(
            "No records found."
        )
